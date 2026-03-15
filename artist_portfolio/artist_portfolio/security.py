from __future__ import annotations

from copy import deepcopy

from csp.constants import NONCE, NONE, SELF


LOGIN_RATE_LIMIT = "5/m"
SENSITIVE_ENDPOINT_RATE_LIMIT = "10/m"
RATE_LIMIT_ERROR_MESSAGE = "Too many requests. Please wait a minute and try again."
ADMIN_CSP_EXCLUDE_PREFIXES = ("/admin/", "/jet/", "/api/schema/")

BASE_CSP_DIRECTIVES = {
    "base-uri": [SELF],
    "connect-src": [SELF],
    "default-src": [SELF],
    "font-src": [SELF, "https://fonts.gstatic.com", "https://cdnjs.cloudflare.com"],
    "form-action": [SELF],
    "frame-ancestors": [SELF],
    "frame-src": [SELF, "https://www.google.com"],
    "img-src": [
        SELF,
        "data:",
        "https://artist-portfolio-media.s3.eu-central-003.backblazeb2.com",
        "https://i.ibb.co",
    ],
    "media-src": [SELF],
    "object-src": [NONE],
    "script-src": [SELF, NONCE, "https://cdnjs.cloudflare.com"],
    "script-src-attr": [NONE],
    "style-src": [
        SELF,
        "https://fonts.googleapis.com",
        "https://cdnjs.cloudflare.com",
        "https://cdn.jsdelivr.net",
    ],
}


def is_production_environment(environment: str) -> bool:
    return environment.lower() == "production"


def build_production_security_settings(
    *,
    environment: str,
    enabled: bool,
) -> dict[str, object]:
    hardening_enabled = is_production_environment(environment) and enabled
    return {
        "SECURE_SSL_REDIRECT": hardening_enabled,
        "SESSION_COOKIE_SECURE": hardening_enabled,
        "CSRF_COOKIE_SECURE": hardening_enabled,
        "SECURE_HSTS_SECONDS": 31536000 if hardening_enabled else 0,
        "SECURE_HSTS_INCLUDE_SUBDOMAINS": hardening_enabled,
        "SECURE_HSTS_PRELOAD": hardening_enabled,
        "SECURE_PROXY_SSL_HEADER": (
            ("HTTP_X_FORWARDED_PROTO", "https") if hardening_enabled else None
        ),
    }


def build_content_security_policy(*, enabled: bool) -> dict[str, object] | None:
    if not enabled:
        return None

    return {
        "EXCLUDE_URL_PREFIXES": ADMIN_CSP_EXCLUDE_PREFIXES,
        "DIRECTIVES": deepcopy(BASE_CSP_DIRECTIVES),
    }
