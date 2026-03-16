import logging

from django.contrib import messages
from django.http import Http404, HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt

from users.models import UserProfile
from .models import Order
from .forms import OrderForm, ShippingForm, PaymentForm, ReceiverForm, CommentForm
from .payment_gateway import (
    InvalidWebhookPayload,
    InvalidWebhookSignature,
    PaymentProviderConfigurationError,
    PaymentProviderError,
)
from .payment_services import (
    PaymentStateError,
    PaymentWebhookProcessingError,
    UnsupportedPaymentMethodError,
    create_checkout_session_for_order,
    process_stripe_webhook,
)


logger = logging.getLogger(__name__)


def get_accessible_order_or_404(request, order_id):
    """
    Return an order only when it is accessible for the current request.
    Otherwise, raise Http404.
    - authenticated user: only own orders
    - guest: only order created in the same session
    """
    if request.user.is_authenticated:
        return get_object_or_404(Order, id=order_id, user=request.user)

    session_key = request.session.session_key
    if not session_key:
        raise Http404("Order not found.")

    return get_object_or_404(Order, id=order_id, user__isnull=True, session_key=session_key)


def order_checkout(request, order_id):
    """
    Ordering: auto-completion of forms, checking the validity of the entered data,
    updating the order and redirecting to the successful checkout page.
    """
    order = get_accessible_order_or_404(request, order_id)
    active_payment = order.active_payment

    if request.GET.get("payment") == "canceled":
        messages.info(
            request,
            "Payment was canceled before confirmation. You can return to checkout and try again.",
        )

    # Filling in the default fields (if the user is logged in)
    if request.user.is_authenticated:
        user_profile = UserProfile.objects.filter(user=request.user).first()
        initial_data = {
            "country": user_profile.country if user_profile else "",
            "address": user_profile.address if user_profile else "",
        }
        receiver_initial = {
            "receiver_name": f"{request.user.first_name} {request.user.last_name}".strip(),
            "receiver_phone": user_profile.phone if user_profile else "",
        }
    else:
        initial_data = {}
        receiver_initial = {}

    # Initializing forms with initial values
    order_form = OrderForm(initial=initial_data)
    shipping_form = ShippingForm(initial={"carrier": order.shipping_carrier})
    payment_form = PaymentForm(initial={"payment_method": order.payment_method})
    receiver_form = ReceiverForm(initial=receiver_initial)
    comment_form = CommentForm()

    if request.method == "POST":
        # Getting data from a POST request
        order_form = OrderForm(request.POST)
        shipping_form = ShippingForm(request.POST)
        payment_form = PaymentForm(request.POST)
        receiver_form = ReceiverForm(request.POST)
        comment_form = CommentForm(request.POST)

        # Validation of all forms
        if all(
            [
                order_form.is_valid(),
                shipping_form.is_valid(),
                payment_form.is_valid(),
                receiver_form.is_valid(),
                comment_form.is_valid(),
            ]
        ):
            if active_payment and active_payment.status in {
                active_payment.STATUS_PAID,
                active_payment.STATUS_REFUNDED,
            }:
                messages.info(request, "This order already has a final payment result.")
                return redirect("orders:order-success", order_id=order.id)

            order.country = order_form.cleaned_data["country"]
            order.address = order_form.cleaned_data["address"]
            order.shipping_carrier = shipping_form.cleaned_data["carrier"]
            order.payment_method = payment_form.cleaned_data["payment_method"]
            order.receiver_name = receiver_form.cleaned_data["receiver_name"]
            order.receiver_phone = receiver_form.cleaned_data["receiver_phone"]
            order.comment = comment_form.cleaned_data["comment"]
            order.save()

            try:
                payment = create_checkout_session_for_order(order, request)
            except UnsupportedPaymentMethodError as exc:
                payment_form.add_error("payment_method", str(exc))
            except PaymentStateError as exc:
                messages.info(request, str(exc))
                return redirect("orders:order-success", order_id=order.id)
            except (PaymentProviderConfigurationError, PaymentProviderError):
                logger.exception("Unable to create provider checkout session.", extra={"order_id": order.id})
                messages.error(
                    request,
                    "Payment checkout is temporarily unavailable. Please try again later.",
                )
            else:
                return redirect(payment.checkout_url)

    return render(
        request,
        "orders/checkout.html",
        {
            "order": order,
            "order_form": order_form,
            "shipping_form": shipping_form,
            "payment_form": payment_form,
            "receiver_form": receiver_form,
            "comment_form": comment_form,
        },
    )


def order_success(request, order_id):
    """
    Display the successful order page.
    """
    order = get_accessible_order_or_404(request, order_id)
    return render(
        request,
        "orders/success.html",
        {"order": order, "payment": order.active_payment},
    )


@csrf_exempt
def stripe_webhook(request):
    """
    Process verified Stripe webhook events and update payment/order state.
    """

    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    signature_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")

    try:
        process_stripe_webhook(payload=request.body, signature_header=signature_header)
    except InvalidWebhookSignature:
        logger.warning("Rejected Stripe webhook due to signature verification failure.")
        return HttpResponse("Invalid Stripe signature.", status=400)
    except InvalidWebhookPayload:
        logger.warning("Rejected Stripe webhook due to malformed payload.")
        return HttpResponse("Invalid Stripe payload.", status=400)
    except PaymentProviderConfigurationError:
        logger.exception("Stripe webhook received while provider settings are incomplete.")
        return HttpResponse("Stripe is not configured.", status=500)
    except PaymentWebhookProcessingError:
        logger.exception("Verified Stripe webhook could not be processed safely.")
        return HttpResponse("Webhook processing failed.", status=500)
    except PaymentProviderError:
        logger.exception("Stripe webhook failed because of a provider communication error.")
        return HttpResponse("Provider communication error.", status=502)

    return HttpResponse(status=200)
