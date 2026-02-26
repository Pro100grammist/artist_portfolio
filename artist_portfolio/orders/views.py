from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.contrib import messages
from users.models import UserProfile
from .models import Order
from .forms import OrderForm, ShippingForm, PaymentForm, ReceiverForm, CommentForm


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
            # Update the order if any data has been changed
            if order_form.has_changed():
                order.country = order_form.cleaned_data["country"]
                order.address = order_form.cleaned_data["address"]

            if shipping_form.has_changed():
                order.shipping_carrier = shipping_form.cleaned_data["carrier"]

            if payment_form.has_changed():
                order.payment_method = payment_form.cleaned_data["payment_method"]

            if receiver_form.has_changed():
                order.receiver_name = receiver_form.cleaned_data["receiver_name"]
                order.receiver_phone = receiver_form.cleaned_data["receiver_phone"]

            if comment_form.has_changed():
                order.comment = comment_form.cleaned_data["comment"]

            order.status = "Pending"
            order.save()

            messages.success(request, "Your order has been successfully placed!")
            return redirect("orders:order-success", order_id=order.id)

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
    return render(request, "orders/success.html", {"order": order})
