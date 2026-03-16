import hashlib
import hmac
import json
import time

import requests
from django.conf import settings


STRIPE_API_BASE = "https://api.stripe.com/v1"


class PaymentProviderError(Exception):
    """Base exception for provider communication errors."""


class PaymentProviderConfigurationError(PaymentProviderError):
    """Raised when provider credentials are missing or invalid."""


class InvalidWebhookPayload(PaymentProviderError):
    """Raised when the webhook payload is malformed."""


class InvalidWebhookSignature(PaymentProviderError):
    """Raised when the webhook signature verification fails."""


def _require_setting(name):
    value = getattr(settings, name, "")
    if not value:
        raise PaymentProviderConfigurationError(
            f"{name} must be configured before live Stripe payments can be used."
        )
    return value


def _stripe_headers(idempotency_key):
    secret_key = _require_setting("STRIPE_SECRET_KEY")
    return {
        "Authorization": f"Bearer {secret_key}",
        "Idempotency-Key": idempotency_key,
    }


def create_checkout_session(*, idempotency_key, payload):
    """
    Create a Stripe Checkout Session through the official HTTPS API.
    """

    try:
        response = requests.post(
            f"{STRIPE_API_BASE}/checkout/sessions",
            headers=_stripe_headers(idempotency_key),
            data=list(payload),
            timeout=10,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise PaymentProviderError("Unable to create Stripe Checkout Session.") from exc

    try:
        data = response.json()
    except ValueError as exc:
        raise PaymentProviderError("Stripe returned a non-JSON response.") from exc

    if "id" not in data or "url" not in data:
        raise PaymentProviderError("Stripe Checkout Session response is missing required fields.")
    return data


def construct_webhook_event(*, payload, signature_header):
    """
    Verify the Stripe signature header and return the parsed JSON event.
    """

    webhook_secret = _require_setting("STRIPE_WEBHOOK_SECRET")
    if not signature_header:
        raise InvalidWebhookSignature("Missing Stripe signature header.")

    timestamp = None
    signatures = []
    for segment in signature_header.split(","):
        if "=" not in segment:
            continue
        key, value = segment.split("=", 1)
        if key == "t":
            timestamp = value
        elif key == "v1":
            signatures.append(value)

    if not timestamp or not signatures:
        raise InvalidWebhookSignature("Stripe signature header is malformed.")

    try:
        timestamp_value = int(timestamp)
    except ValueError as exc:
        raise InvalidWebhookSignature("Stripe signature timestamp is invalid.") from exc

    tolerance = int(settings.STRIPE_WEBHOOK_TOLERANCE)
    signed_payload = timestamp.encode("utf-8") + b"." + payload
    expected_signature = hmac.new(
        webhook_secret.encode("utf-8"),
        signed_payload,
        hashlib.sha256,
    ).hexdigest()

    is_valid_signature = any(
        hmac.compare_digest(expected_signature, signature) for signature in signatures
    )
    if not is_valid_signature:
        raise InvalidWebhookSignature("Stripe signature verification failed.")

    current_timestamp = int(time.time())
    if abs(current_timestamp - timestamp_value) > tolerance:
        raise InvalidWebhookSignature("Stripe webhook signature is outside the tolerance window.")

    try:
        event = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InvalidWebhookPayload("Webhook body is not valid JSON.") from exc

    if "id" not in event or "type" not in event:
        raise InvalidWebhookPayload("Webhook body is missing the Stripe event envelope.")

    return event
