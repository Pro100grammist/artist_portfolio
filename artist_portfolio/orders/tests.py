import hashlib
import hmac
import json
import time
from decimal import Decimal
from unittest import mock

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from store.models import Category, Product

from .models import Order, OrderItem, OrderPayment, PaymentEvent


def build_stripe_signature(payload, secret, timestamp=None):
    timestamp = timestamp or int(time.time())
    signed_payload = str(timestamp).encode("utf-8") + b"." + payload
    signature = hmac.new(
        secret.encode("utf-8"),
        signed_payload,
        hashlib.sha256,
    ).hexdigest()
    return f"t={timestamp},v1={signature}"


class OrderAccessControlTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", password="pass12345")
        self.user2 = User.objects.create_user(username="user2", password="pass12345")

        self.user1_order = Order.objects.create(user=self.user1, total_price=100)
        self.user2_order = Order.objects.create(user=self.user2, total_price=150)

    def test_owner_can_access_checkout(self):
        self.client.login(username="user1", password="pass12345")
        response = self.client.get(
            reverse("orders:order-checkout", args=[self.user1_order.id])
        )
        self.assertEqual(response.status_code, 200)

    def test_other_user_cannot_access_checkout(self):
        self.client.login(username="user2", password="pass12345")
        response = self.client.get(
            reverse("orders:order-checkout", args=[self.user1_order.id])
        )
        self.assertEqual(response.status_code, 404)

    def test_owner_can_access_success(self):
        self.client.login(username="user1", password="pass12345")
        response = self.client.get(
            reverse("orders:order-success", args=[self.user1_order.id])
        )
        self.assertEqual(response.status_code, 200)

    def test_other_user_cannot_access_success(self):
        self.client.login(username="user2", password="pass12345")
        response = self.client.get(
            reverse("orders:order-success", args=[self.user1_order.id])
        )
        self.assertEqual(response.status_code, 404)


class GuestOrderAccessControlTests(TestCase):
    def test_guest_can_access_only_same_session_order(self):
        session = self.client.session
        if not session.session_key:
            session.save()
        session_key = session.session_key

        guest_order = Order.objects.create(session_key=session_key, total_price=50)

        response_ok = self.client.get(
            reverse("orders:order-checkout", args=[guest_order.id])
        )
        self.assertEqual(response_ok.status_code, 200)

        other_client = self.client_class()
        response_forbidden = other_client.get(
            reverse("orders:order-checkout", args=[guest_order.id])
        )
        self.assertEqual(response_forbidden.status_code, 404)


@override_settings(
    STRIPE_SECRET_KEY="sk_test_checkout",
    STRIPE_WEBHOOK_SECRET="whsec_checkout",
    PAYMENT_DEFAULT_CURRENCY="usd",
)
class CheckoutPaymentFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="checkout-user",
            email="checkout@example.com",
            password="pass12345",
        )
        self.category = Category.objects.create(name="Paintings")
        self.product = Product.objects.create(
            name="Blue Horizon",
            price=Decimal("120.00"),
            category=self.category,
            is_available=True,
        )
        self.order = Order.objects.create(user=self.user, total_price=Decimal("240.00"))
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            price=self.product.price,
        )
        self.client.login(username="checkout-user", password="pass12345")

    def _checkout_payload(self, payment_method="credit_card"):
        return {
            "country": "US",
            "address": "1 Payment Street",
            "carrier": "dhl",
            "payment_method": payment_method,
            "receiver_name": "Checkout User",
            "receiver_phone": "+12025550111",
            "comment": "Leave at the front desk",
        }

    @mock.patch("orders.payment_gateway.requests.post")
    def test_checkout_post_creates_pending_payment_and_redirects_to_stripe(self, mocked_post):
        mocked_response = mock.Mock()
        mocked_response.raise_for_status.return_value = None
        mocked_response.json.return_value = {
            "id": "cs_test_123",
            "url": "https://checkout.stripe.com/c/pay/cs_test_123",
            "payment_intent": "pi_test_123",
        }
        mocked_post.return_value = mocked_response

        response = self.client.post(
            reverse("orders:order-checkout", args=[self.order.id]),
            data=self._checkout_payload(),
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response["Location"],
            "https://checkout.stripe.com/c/pay/cs_test_123",
        )

        payment = OrderPayment.objects.get(order=self.order)
        self.order.refresh_from_db()

        self.assertEqual(payment.status, OrderPayment.STATUS_PENDING)
        self.assertEqual(payment.provider_checkout_session_id, "cs_test_123")
        self.assertEqual(payment.provider_payment_intent_id, "pi_test_123")
        self.assertEqual(payment.currency, "usd")
        self.assertEqual(payment.amount, Decimal("240.00"))
        self.assertEqual(
            payment.idempotency_key,
            f"order-{self.order.id}-stripe-checkout-attempt-1",
        )
        self.assertEqual(self.order.status, Order.STATUS_AWAITING_PAYMENT)
        self.assertEqual(self.order.payment_method, "credit_card")

        mocked_post.assert_called_once()
        self.assertEqual(
            mocked_post.call_args.kwargs["headers"]["Idempotency-Key"],
            payment.idempotency_key,
        )


@override_settings(
    STRIPE_SECRET_KEY="sk_test_webhook",
    STRIPE_WEBHOOK_SECRET="whsec_test_webhook",
    PAYMENT_DEFAULT_CURRENCY="usd",
    STRIPE_WEBHOOK_TOLERANCE=300,
)
class StripeWebhookLifecycleTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="webhook-user",
            email="webhook@example.com",
            password="pass12345",
        )
        self.category = Category.objects.create(name="Abstract")
        self.product = Product.objects.create(
            name="Golden Hour",
            price=Decimal("150.00"),
            category=self.category,
            is_available=True,
        )
        self.order = Order.objects.create(user=self.user, total_price=Decimal("150.00"))
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=1,
            price=self.product.price,
        )
        self.payment = OrderPayment.objects.create(
            order=self.order,
            provider=OrderPayment.PROVIDER_STRIPE,
            amount=self.order.total_price,
            currency="usd",
            attempt_number=1,
            idempotency_key="order-1-stripe-checkout-attempt-1",
            provider_checkout_session_id="cs_test_123",
            provider_payment_intent_id="pi_test_123",
            checkout_url="https://checkout.stripe.com/c/pay/cs_test_123",
            status=OrderPayment.STATUS_PENDING,
            is_active=True,
        )

    def _post_webhook(self, event, signature=None):
        payload = json.dumps(event).encode("utf-8")
        signature = signature or build_stripe_signature(
            payload,
            settings.STRIPE_WEBHOOK_SECRET,
        )
        return self.client.post(
            reverse("orders:stripe-webhook"),
            data=payload,
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE=signature,
        )

    def _checkout_completed_event(self, event_id="evt_checkout_completed"):
        return {
            "id": event_id,
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "object": "checkout.session",
                    "id": self.payment.provider_checkout_session_id,
                    "payment_intent": self.payment.provider_payment_intent_id,
                    "payment_status": "paid",
                    "amount_total": 15000,
                    "currency": "usd",
                    "metadata": {
                        "order_id": str(self.order.id),
                        "payment_id": str(self.payment.id),
                        "attempt_number": str(self.payment.attempt_number),
                    },
                }
            },
        }

    def _payment_failed_event(self, event_id="evt_payment_failed"):
        return {
            "id": event_id,
            "type": "payment_intent.payment_failed",
            "data": {
                "object": {
                    "object": "payment_intent",
                    "id": self.payment.provider_payment_intent_id,
                    "amount": 15000,
                    "currency": "usd",
                    "metadata": {
                        "order_id": str(self.order.id),
                        "payment_id": str(self.payment.id),
                        "attempt_number": str(self.payment.attempt_number),
                    },
                }
            },
        }

    def test_webhook_signature_failure_returns_400(self):
        event = self._checkout_completed_event()
        payload = json.dumps(event).encode("utf-8")
        invalid_signature = f"t={int(time.time())},v1=invalid"

        response = self.client.post(
            reverse("orders:stripe-webhook"),
            data=payload,
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE=invalid_signature,
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(PaymentEvent.objects.count(), 0)

    def test_success_event_marks_payment_and_order_paid(self):
        response = self._post_webhook(self._checkout_completed_event())

        self.assertEqual(response.status_code, 200)
        self.payment.refresh_from_db()
        self.order.refresh_from_db()

        self.assertEqual(self.payment.status, OrderPayment.STATUS_PAID)
        self.assertIsNotNone(self.payment.paid_at)
        self.assertEqual(self.order.status, Order.STATUS_PAID)

        event_log = PaymentEvent.objects.get(provider_event_id="evt_checkout_completed")
        self.assertTrue(event_log.processed)

    def test_webhook_replay_is_idempotent(self):
        event = self._checkout_completed_event(event_id="evt_duplicate")

        first_response = self._post_webhook(event)
        self.payment.refresh_from_db()
        first_paid_at = self.payment.paid_at

        second_response = self._post_webhook(event)

        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(second_response.status_code, 200)
        self.assertEqual(PaymentEvent.objects.count(), 1)

        self.payment.refresh_from_db()
        self.order.refresh_from_db()
        self.assertEqual(self.payment.status, OrderPayment.STATUS_PAID)
        self.assertEqual(self.order.status, Order.STATUS_PAID)
        self.assertEqual(self.payment.paid_at, first_paid_at)

    def test_failed_event_does_not_mark_order_paid(self):
        response = self._post_webhook(self._payment_failed_event())

        self.assertEqual(response.status_code, 200)
        self.payment.refresh_from_db()
        self.order.refresh_from_db()

        self.assertEqual(self.payment.status, OrderPayment.STATUS_FAILED)
        self.assertIsNone(self.payment.paid_at)
        self.assertEqual(self.order.status, Order.STATUS_AWAITING_PAYMENT)
        self.assertNotEqual(self.order.status, Order.STATUS_PAID)
