import requests

from django.conf import settings


def send_whatsapp_message(client_email, message):
    """
    Sends a WhatsApp notification using the CallMeBot API (temporarily).

    Args:
        client_email (str): The email of the client who submitted the message.
        message (str): The content of the message.

    Returns:
        None
    """
    API_KEY = settings.API_KEY  # callmebot API-key
    PHONE_NUMBER = settings.PHONE_NUMBER  # # Recipient's phone number

    full_message = f"You have received a message from ArtistPortfolio:\nFrom: {client_email}\nMessage: {message}"

    url = f"https://api.callmebot.com/whatsapp.php?phone={PHONE_NUMBER}&text={full_message}&apikey={API_KEY}"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("WhatsApp message has been successfully sent!")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Sending error WhatsApp: {e}")
