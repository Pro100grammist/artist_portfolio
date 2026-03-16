import hashlib
import logging
from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.db import IntegrityError, transaction
from django.db.models import Max
from django.urls import reverse
from django.utils import timezone

from .models import Order, OrderPayment, PaymentEvent
from .payment_gateway import construct_webhook_event, create_checkout_session


logger = logging.getLogger(__name__)


class UnsupportedPaymentMethodError(Exception):
    """Raised when a checkout request selects a non-live payment method."""


class PaymentStateError(Exception):
    """Raised when checkout is attempted for an order that should not be charged again."""


class PaymentWebhookProcessingError(Exception):
    """Raised when a verified webhook cannot be processed safely."""


STRIPE_PROVIDER = OrderPayment.PROVIDER_STRIPE
SUPPORTED_CHECKOUT_PAYMENT_METHODS = {"credit_card", "google_pay"}
ALLOWED_STRIPE_EVENT_TYPES = {
    "checkout.session.completed",
    "checkout.session.async_payment_succeeded",
    "checkout.session.async_payment_failed",
    "checkout.session.expired",
    "payment_intent.payment_failed",
    "payment_intent.canceled",
    "charge.refunded",
}
ZERO_DECIMAL_CURRENCIES = {
    "bif",
    "clp",
    "djf",
    "gnf",
    "jpy",
    "kmf",
    "krw",
    "mga",
    "pyg",
    "rwf",
    "ugx",
    "vnd",
    "vuv",
    "xaf",
    "xof",
    "xpf",
}
ALLOWED_PAYMENT_STATUS_TRANSITIONS = {
    OrderPayment.STATUS_CREATED: {
        OrderPayment.STATUS_PENDING,
        OrderPayment.STATUS_PAID,
        OrderPayment.STATUS_FAILED,
        OrderPayment.STATUS_CANCELED,
    },
    OrderPayment.STATUS_PENDING: {
        OrderPayment.STATUS_PAID,
        OrderPayment.STATUS_FAILED,
        OrderPayment.STATUS_CANCELED,
    },
    OrderPayment.STATUS_PAID: {OrderPayment.STATUS_REFUNDED},
    OrderPayment.STATUS_FAILED: set(),
    OrderPayment.STATUS_CANCELED: set(),
    OrderPayment.STATUS_REFUNDED: set(),
}


def amount_to_minor_units(amount, currency):
    quantized = Decimal(amount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    normalized_currency = currency.lower()
    if normalized_currency in ZERO_DECIMAL_CURRENCIES:
        return int(quantized.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    return int((quantized * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def build_idempotency_key(order_id, attempt_number):
    return f"order-{order_id}-stripe-checkout-attempt-{attempt_number}"


def build_checkout_session_payload(*, order, payment, success_url, cancel_url):
    payload = [
        ("mode", "payment"),
        ("success_url", success_url),
        ("cancel_url", cancel_url),
        ("client_reference_id", str(order.id)),
        ("metadata[order_id]", str(order.id)),
        ("metadata[payment_id]", str(payment.id)),
        ("metadata[attempt_number]", str(payment.attempt_number)),
        ("payment_intent_data[metadata][order_id]", str(order.id)),
        ("payment_intent_data[metadata][payment_id]", str(payment.id)),
        ("payment_intent_data[metadata][attempt_number]", str(payment.attempt_number)),
        ("billing_address_collection", "auto"),
        ("submit_type", "pay"),
    ]

    if order.user and order.user.email:
        payload.append(("customer_email", order.user.email))

    for index, item in enumerate(order.items.select_related("product")):
        payload.extend(
            [
                (
                    f"line_items[{index}][price_data][currency]",
                    payment.currency.lower(),
                ),
                (
                    f"line_items[{index}][price_data][unit_amount]",
                    str(amount_to_minor_units(item.price, payment.currency)),
                ),
                (
                    f"line_items[{index}][price_data][product_data][name]",
                    item.product.name,
                ),
                (f"line_items[{index}][quantity]", str(item.quantity)),
            ]
        )

    return payload


def _ensure_checkout_can_be_started(order):
    if order.payments.filter(status=OrderPayment.STATUS_PAID).exists():
        raise PaymentStateError("This order already has a verified paid payment.")

    if order.payments.filter(status=OrderPayment.STATUS_REFUNDED).exists():
        raise PaymentStateError("Refunded orders cannot be charged again.")

    if order.payment_method not in SUPPORTED_CHECKOUT_PAYMENT_METHODS:
        raise UnsupportedPaymentMethodError(
            "The selected payment method is not available for live Stripe checkout."
        )

    if not order.items.exists():
        raise PaymentStateError("Orders without items cannot be sent to checkout.")


def _next_attempt_number(order):
    max_attempt = (
        order.payments.filter(provider=STRIPE_PROVIDER).aggregate(
            max_attempt=Max("attempt_number")
        )["max_attempt"]
        or 0
    )
    return max_attempt + 1


def _create_or_reuse_active_payment(order):
    active_payment = (
        order.payments.filter(
            provider=STRIPE_PROVIDER,
            is_active=True,
            status__in=[OrderPayment.STATUS_CREATED, OrderPayment.STATUS_PENDING],
        )
        .order_by("-created_at")
        .first()
    )
    if active_payment:
        return active_payment, False

    attempt_number = _next_attempt_number(order)
    order.payments.filter(provider=STRIPE_PROVIDER, is_active=True).update(is_active=False)
    payment = OrderPayment.objects.create(
        order=order,
        provider=STRIPE_PROVIDER,
        amount=order.total_price,
        currency=settings.PAYMENT_DEFAULT_CURRENCY.lower(),
        attempt_number=attempt_number,
        idempotency_key=build_idempotency_key(order.id, attempt_number),
        status=OrderPayment.STATUS_CREATED,
        is_active=True,
    )
    return payment, True


def create_checkout_session_for_order(order, request):
    """
    Create or reuse an active Stripe Checkout Session for the order.
    """

    _ensure_checkout_can_be_started(order)
    payment, _ = _create_or_reuse_active_payment(order)

    if order.status != Order.STATUS_AWAITING_PAYMENT:
        order.status = Order.STATUS_AWAITING_PAYMENT
        order.save(update_fields=["status", "updated_at"])

    if payment.checkout_url and payment.status == OrderPayment.STATUS_PENDING:
        return payment

    success_url = request.build_absolute_uri(
        reverse("orders:order-success", args=[order.id])
    )
    success_url = f"{success_url}?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = request.build_absolute_uri(
        reverse("orders:order-checkout", args=[order.id])
    )
    cancel_url = f"{cancel_url}?payment=canceled"

    session_data = create_checkout_session(
        idempotency_key=payment.idempotency_key,
        payload=build_checkout_session_payload(
            order=order,
            payment=payment,
            success_url=success_url,
            cancel_url=cancel_url,
        ),
    )

    payment.status = OrderPayment.STATUS_PENDING
    payment.provider_checkout_session_id = session_data["id"]
    payment.provider_payment_intent_id = session_data.get("payment_intent") or None
    payment.checkout_url = session_data["url"]
    payment.raw_last_event = {
        "type": "checkout.session.created",
        "data": {"object": session_data},
    }
    payment.save(
        update_fields=[
            "status",
            "provider_checkout_session_id",
            "provider_payment_intent_id",
            "checkout_url",
            "raw_last_event",
            "updated_at",
        ]
    )
    return payment


def process_stripe_webhook(*, payload, signature_header):
    """
    Verify and process a Stripe webhook event.
    """

    event = construct_webhook_event(payload=payload, signature_header=signature_header)
    if event["type"] not in ALLOWED_STRIPE_EVENT_TYPES:
        logger.info("Ignoring Stripe webhook event outside the allowlist.", extra={"event_type": event["type"]})
        return {"status": "ignored", "event_type": event["type"]}

    return _process_verified_stripe_event(event=event, raw_payload=payload)


def _process_verified_stripe_event(*, event, raw_payload):
    payload_hash = hashlib.sha256(raw_payload).hexdigest()
    event_log = _get_or_create_event_log(event=event, raw_payload=raw_payload, payload_hash=payload_hash)

    if event_log.payload_hash != payload_hash:
        PaymentEvent.objects.filter(pk=event_log.pk).update(
            processing_error="Received the same provider event id with a different payload hash.",
        )
        raise PaymentWebhookProcessingError(
            "Stripe event id replayed with a different payload hash."
        )

    if event_log.processed:
        return {"status": "duplicate", "event_type": event["type"]}

    try:
        with transaction.atomic():
            locked_event_log = PaymentEvent.objects.select_for_update().get(pk=event_log.pk)
            if locked_event_log.processed:
                return {"status": "duplicate", "event_type": event["type"]}

            payment = _resolve_payment_for_event(event)
            target_status = _map_event_to_payment_status(event)
            _maybe_attach_provider_ids(payment, event)

            if target_status in {OrderPayment.STATUS_PAID, OrderPayment.STATUS_REFUNDED}:
                _validate_amount_and_currency(payment, event)

            _transition_payment(payment, target_status=target_status, event=event)

            locked_event_log.processed = True
            locked_event_log.processed_at = timezone.now()
            locked_event_log.processing_error = ""
            locked_event_log.save(
                update_fields=["processed", "processed_at", "processing_error"]
            )
    except Exception as exc:
        PaymentEvent.objects.filter(pk=event_log.pk).update(
            processing_error=str(exc),
        )
        raise PaymentWebhookProcessingError(str(exc)) from exc

    return {"status": "processed", "event_type": event["type"]}


def _get_or_create_event_log(*, event, raw_payload, payload_hash):
    defaults = {
        "event_type": event["type"],
        "payload_hash": payload_hash,
        "raw_payload": raw_payload.decode("utf-8", errors="replace"),
    }
    try:
        event_log, _ = PaymentEvent.objects.get_or_create(
            provider=STRIPE_PROVIDER,
            provider_event_id=event["id"],
            defaults=defaults,
        )
    except IntegrityError:
        event_log = PaymentEvent.objects.get(
            provider=STRIPE_PROVIDER,
            provider_event_id=event["id"],
        )

    if not event_log.raw_payload:
        event_log.raw_payload = defaults["raw_payload"]
        event_log.save(update_fields=["raw_payload"])
    if not event_log.event_type:
        event_log.event_type = event["type"]
        event_log.save(update_fields=["event_type"])
    return event_log


def _resolve_payment_for_event(event):
    data = event.get("data", {}).get("object", {})
    metadata = data.get("metadata") or {}
    object_type = data.get("object")
    checkout_session_id = data.get("id") if object_type == "checkout.session" else None
    payment_intent_id = None
    if object_type == "payment_intent":
        payment_intent_id = data.get("id")
    elif object_type == "charge":
        payment_intent_id = data.get("payment_intent")
    else:
        payment_intent_id = data.get("payment_intent")

    payment = None
    if checkout_session_id:
        payment = OrderPayment.objects.select_related("order").filter(
            provider_checkout_session_id=checkout_session_id
        ).first()
    if not payment and payment_intent_id:
        payment = OrderPayment.objects.select_related("order").filter(
            provider_payment_intent_id=payment_intent_id
        ).first()
    if not payment and metadata.get("payment_id"):
        payment = OrderPayment.objects.select_related("order").filter(
            pk=metadata["payment_id"]
        ).first()

    if not payment:
        raise PaymentWebhookProcessingError("No matching order payment was found for the Stripe event.")
    return payment


def _map_event_to_payment_status(event):
    event_type = event["type"]
    data = event.get("data", {}).get("object", {})

    if event_type == "checkout.session.completed":
        if data.get("payment_status") in {"paid", "no_payment_required"}:
            return OrderPayment.STATUS_PAID
        return OrderPayment.STATUS_PENDING
    if event_type == "checkout.session.async_payment_succeeded":
        return OrderPayment.STATUS_PAID
    if event_type in {
        "checkout.session.async_payment_failed",
        "payment_intent.payment_failed",
    }:
        return OrderPayment.STATUS_FAILED
    if event_type in {"checkout.session.expired", "payment_intent.canceled"}:
        return OrderPayment.STATUS_CANCELED
    if event_type == "charge.refunded":
        if not data.get("refunded") and not data.get("amount_refunded"):
            raise PaymentWebhookProcessingError(
                "Refund webhook did not include refunded charge details."
            )
        return OrderPayment.STATUS_REFUNDED

    raise PaymentWebhookProcessingError(f"Unsupported Stripe event type: {event_type}")


def _maybe_attach_provider_ids(payment, event):
    data = event.get("data", {}).get("object", {})
    object_type = data.get("object")
    updated_fields = []

    if object_type == "checkout.session":
        session_id = data.get("id")
        payment_intent_id = data.get("payment_intent")
        if session_id and payment.provider_checkout_session_id != session_id:
            payment.provider_checkout_session_id = session_id
            updated_fields.append("provider_checkout_session_id")
        if payment_intent_id and payment.provider_payment_intent_id != payment_intent_id:
            payment.provider_payment_intent_id = payment_intent_id
            updated_fields.append("provider_payment_intent_id")
    elif object_type == "payment_intent":
        payment_intent_id = data.get("id")
        if payment_intent_id and payment.provider_payment_intent_id != payment_intent_id:
            payment.provider_payment_intent_id = payment_intent_id
            updated_fields.append("provider_payment_intent_id")
    elif object_type == "charge":
        payment_intent_id = data.get("payment_intent")
        if payment_intent_id and payment.provider_payment_intent_id != payment_intent_id:
            payment.provider_payment_intent_id = payment_intent_id
            updated_fields.append("provider_payment_intent_id")

    if updated_fields:
        updated_fields.append("updated_at")
        payment.save(update_fields=updated_fields)


def _validate_amount_and_currency(payment, event):
    expected_amount = amount_to_minor_units(payment.amount, payment.currency)
    order_amount = amount_to_minor_units(payment.order.total_price, payment.currency)
    data = event.get("data", {}).get("object", {})
    object_type = data.get("object")

    if object_type == "checkout.session":
        event_amount = data.get("amount_total")
    elif object_type == "payment_intent":
        event_amount = data.get("amount")
    elif object_type == "charge":
        event_amount = data.get("amount")
    else:
        raise PaymentWebhookProcessingError("Unsupported Stripe object for amount verification.")

    event_currency = (data.get("currency") or "").lower()
    if event_amount is None or not event_currency:
        raise PaymentWebhookProcessingError("Stripe event is missing amount or currency data.")

    if expected_amount != event_amount or order_amount != event_amount:
        raise PaymentWebhookProcessingError(
            f"Stripe amount mismatch for order {payment.order_id}: expected {expected_amount}, received {event_amount}."
        )

    if payment.currency.lower() != event_currency:
        raise PaymentWebhookProcessingError(
            f"Stripe currency mismatch for order {payment.order_id}: expected {payment.currency.lower()}, received {event_currency}."
        )


def _transition_payment(payment, *, target_status, event):
    if target_status == payment.status:
        payment.raw_last_event = event
        update_fields = ["raw_last_event", "updated_at"]
        if target_status == OrderPayment.STATUS_PAID and not payment.paid_at:
            payment.paid_at = timezone.now()
            update_fields.append("paid_at")
        payment.save(update_fields=update_fields)
        _sync_order_status_from_payment(payment)
        return

    allowed_transitions = ALLOWED_PAYMENT_STATUS_TRANSITIONS[payment.status]
    if target_status not in allowed_transitions:
        logger.info(
            "Ignoring non-forward payment transition.",
            extra={
                "payment_id": payment.id,
                "current_status": payment.status,
                "target_status": target_status,
                "event_type": event["type"],
            },
        )
        payment.raw_last_event = event
        payment.save(update_fields=["raw_last_event", "updated_at"])
        return

    payment.status = target_status
    payment.raw_last_event = event
    update_fields = ["status", "raw_last_event", "updated_at"]

    if target_status == OrderPayment.STATUS_PAID:
        payment.paid_at = timezone.now()
        update_fields.append("paid_at")

    payment.save(update_fields=update_fields)
    _sync_order_status_from_payment(payment)


def _sync_order_status_from_payment(payment):
    order = payment.order
    has_paid_payment = order.payments.filter(status=OrderPayment.STATUS_PAID).exists()

    if payment.status == OrderPayment.STATUS_PAID:
        order.payments.exclude(pk=payment.pk).update(is_active=False)
        if not payment.is_active:
            payment.is_active = True
            payment.save(update_fields=["is_active", "updated_at"])
        target_status = Order.STATUS_PAID
    elif payment.status == OrderPayment.STATUS_REFUNDED:
        order.payments.exclude(pk=payment.pk).update(is_active=False)
        if not payment.is_active:
            payment.is_active = True
            payment.save(update_fields=["is_active", "updated_at"])
        target_status = Order.STATUS_REFUNDED
    elif payment.status == OrderPayment.STATUS_CANCELED:
        if not payment.is_active or has_paid_payment:
            return
        target_status = Order.STATUS_CANCELLED
    elif payment.status in {
        OrderPayment.STATUS_CREATED,
        OrderPayment.STATUS_PENDING,
        OrderPayment.STATUS_FAILED,
    }:
        if not payment.is_active or has_paid_payment:
            return
        target_status = Order.STATUS_AWAITING_PAYMENT
    else:
        return

    if order.status != target_status:
        order.status = target_status
        order.save(update_fields=["status", "updated_at"])
