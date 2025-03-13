import qrcode
import base64
from io import BytesIO


def generate_qr_code(secret):
    """
    Generates a QR code with the passed secret key and returns it in base64 format.

    :param secret: The secret key used to generate the QR code.
    :return: The QR code as a base64 string.
    """
    qr = qrcode.make(secret)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()
