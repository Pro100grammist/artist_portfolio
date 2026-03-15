from unittest.mock import patch

from django.core.cache import cache
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from artist_portfolio.security import (
    RATE_LIMIT_ERROR_MESSAGE,
    build_content_security_policy,
    build_production_security_settings,
)


class SecurityConfigurationTests(SimpleTestCase):
    def test_production_security_settings_are_enabled_in_production(self):
        security_settings = build_production_security_settings(
            environment="production",
            enabled=True,
        )

        self.assertTrue(security_settings["SECURE_SSL_REDIRECT"])
        self.assertTrue(security_settings["SESSION_COOKIE_SECURE"])
        self.assertTrue(security_settings["CSRF_COOKIE_SECURE"])
        self.assertEqual(security_settings["SECURE_HSTS_SECONDS"], 31536000)
        self.assertTrue(security_settings["SECURE_HSTS_INCLUDE_SUBDOMAINS"])
        self.assertTrue(security_settings["SECURE_HSTS_PRELOAD"])
        self.assertEqual(
            security_settings["SECURE_PROXY_SSL_HEADER"],
            ("HTTP_X_FORWARDED_PROTO", "https"),
        )

    def test_production_security_settings_are_disabled_outside_production(self):
        security_settings = build_production_security_settings(
            environment="development",
            enabled=True,
        )

        self.assertFalse(security_settings["SECURE_SSL_REDIRECT"])
        self.assertFalse(security_settings["SESSION_COOKIE_SECURE"])
        self.assertFalse(security_settings["CSRF_COOKIE_SECURE"])
        self.assertEqual(security_settings["SECURE_HSTS_SECONDS"], 0)
        self.assertFalse(security_settings["SECURE_HSTS_INCLUDE_SUBDOMAINS"])
        self.assertFalse(security_settings["SECURE_HSTS_PRELOAD"])
        self.assertIsNone(security_settings["SECURE_PROXY_SSL_HEADER"])

    def test_content_security_policy_contains_required_directives(self):
        policy = build_content_security_policy(enabled=True)
        directives = policy["DIRECTIVES"]

        self.assertIn("default-src", directives)
        self.assertIn("script-src", directives)
        self.assertIn("style-src", directives)
        self.assertIn("img-src", directives)
        self.assertIn("font-src", directives)
        self.assertIn("connect-src", directives)
        self.assertIn("frame-ancestors", directives)
        self.assertIn("/admin/", policy["EXCLUDE_URL_PREFIXES"])


@override_settings(RATELIMIT_ENABLE=True)
class ContactRateLimitTests(TestCase):
    def setUp(self):
        cache.clear()
        self.url = reverse("submit_contact")
        self.payload = {
            "name": "Rate Limited User",
            "email": "limited@example.com",
            "subject": "Need help",
            "message": "Hello from the contact form.",
        }

    def tearDown(self):
        cache.clear()

    @patch("core.views.send_whatsapp_message")
    @patch("core.views.send_mail")
    def test_contact_form_returns_429_after_ten_requests(
        self,
        send_mail_mock,
        send_whatsapp_mock,
    ):
        send_mail_mock.return_value = 1
        send_whatsapp_mock.return_value = None

        for _ in range(10):
            response = self.client.post(self.url, self.payload)
            self.assertEqual(response.status_code, 302)

        response = self.client.post(self.url, self.payload)

        self.assertEqual(response.status_code, 429)
        self.assertContains(
            response,
            RATE_LIMIT_ERROR_MESSAGE,
            status_code=429,
        )
