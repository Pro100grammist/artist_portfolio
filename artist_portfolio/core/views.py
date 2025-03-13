from random import sample

from django.core.mail import send_mail
from django.shortcuts import render, redirect

from .models import Artwork, ContactMessage
from .utils import send_whatsapp_message


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
