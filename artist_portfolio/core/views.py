from random import sample

from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from django_ratelimit.decorators import ratelimit

from .models import Artwork, ContactMessage
from .utils import send_whatsapp_message
from artist_portfolio.security import (
    RATE_LIMIT_ERROR_MESSAGE,
    SENSITIVE_ENDPOINT_RATE_LIMIT,
)


def home(request):
    """
    Renders the homepage with up to 10 random artworks in gallery block.
    """
    all_ids = Artwork.objects.values_list('id', flat=True)
    random_ids = sample(list(all_ids), min(len(all_ids), 10)) # Select up to 10 random artworks for swiper
    artworks = Artwork.objects.filter(id__in=random_ids)
    return render(request, "core/home.html", {"artworks": artworks})


def about(request):
    """
    View for the 'About' page.
    """
    return render(request, "core/about.html")


def contact(request):
    """
    View for the 'Contact' page.
    """
    return render(request, 'core/contact.html')


@ratelimit(key="ip", rate=SENSITIVE_ENDPOINT_RATE_LIMIT, method="POST")
def submit_contact_form(request):
    """
    Handles the contact form submission.
    Saves the message in the database and sends email + WhatsApp notification.
    """
    if request.method == "POST":
        name = request.POST.get("name", "Anonymous")
        subject = request.POST.get("subject", "New request from the contact form")
        message = request.POST.get("message", "")
        client_email = request.POST.get("email", "")

        # Debugging log
        # print(f"Email: {client_email}, Message: {message}")

        try:
            # Saving a message in the database
            ContactMessage.objects.create(
                name=name, email=client_email, message=message
            )
            # Send an email notification
            send_mail(
                subject,
                message=f"Message from {client_email}:\n{message}",
                from_email="senpyinteractive@gmail.com",
                recipient_list=["senpyinteractive@gmail.com"],
                fail_silently=False,
            )

            # Send a WhatsApp notification (if implemented)
            send_whatsapp_message(client_email, message)

            return redirect("contact_success")
        except Exception as e:
            return render(
                request, "contact_success.html", {"error_message": f"Error: {e}"}
            )

    return render(request, "core/contact.html")


def contact_success(request):
    return render(request, 'contact_success.html')


def _wants_json_response(request):
    accept_header = request.headers.get("Accept", "")
    return (
        request.headers.get("X-Requested-With") == "XMLHttpRequest"
        or "application/json" in accept_header
    )


def rate_limited(request, exception):
    if _wants_json_response(request):
        return JsonResponse({"error": RATE_LIMIT_ERROR_MESSAGE}, status=429)

    if request.path == reverse("users:login"):
        from users.forms import CustomAuthenticationForm

        form = CustomAuthenticationForm(request=request, data=request.POST or None)
        form.add_error(None, RATE_LIMIT_ERROR_MESSAGE)
        return render(request, "users/login.html", {"form": form}, status=429)

    if request.path == reverse("submit_contact"):
        return render(
            request,
            "contact_success.html",
            {"error_message": RATE_LIMIT_ERROR_MESSAGE},
            status=429,
        )

    cart_root = reverse("cart:cart")
    if request.path.startswith(cart_root):
        from cart.views import get_or_create_cart

        return render(
            request,
            "cart/cart.html",
            {
                "cart": get_or_create_cart(request),
                "rate_limit_error": RATE_LIMIT_ERROR_MESSAGE,
            },
            status=429,
        )

    return render(
        request,
        "contact_success.html",
        {"error_message": RATE_LIMIT_ERROR_MESSAGE},
        status=429,
    )
