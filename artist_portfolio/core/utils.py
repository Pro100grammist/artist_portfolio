import requests
from django.conf import settings


def send_whatsapp_message(client_email, message):
    """
    Sends a WhatsApp notification using CallMeBot API.
    """
    api_key = settings.API_KEY
    phone_number = settings.PHONE_NUMBER

    text = (
        "You have received a message from ArtistPortfolio:\n"
        f"From: {client_email}\n"
        f"Message: {message}"
    )

    params = {
        "phone": phone_number,
        "text": text,
        "apikey": api_key,
    }

    try:
        response = requests.get(
            "https://api.callmebot.com/whatsapp.php",
            params=params,
            timeout=5,
        )
        if response.status_code == 200:
            print("WhatsApp message has been successfully sent!")
        else:
            print(f"WhatsApp API error ({response.status_code}): {response.text}")
    except requests.RequestException as exc:
        print(f"Sending WhatsApp failed: {exc}")
