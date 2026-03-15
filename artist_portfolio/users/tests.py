from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from artist_portfolio.security import RATE_LIMIT_ERROR_MESSAGE


@override_settings(RATELIMIT_ENABLE=True)
class LoginRateLimitTests(TestCase):
    def setUp(self):
        cache.clear()
        self.url = reverse("users:login")
        self.user = User.objects.create_user(
            username="limited-user",
            password="strong-pass-123",
        )

    def tearDown(self):
        cache.clear()

    def test_login_returns_429_after_five_attempts(self):
        payload = {
            "username": self.user.username,
            "password": "wrong-password",
        }

        for _ in range(5):
            response = self.client.post(self.url, payload)
            self.assertEqual(response.status_code, 200)

        response = self.client.post(self.url, payload)

        self.assertEqual(response.status_code, 429)
        self.assertContains(
            response,
            RATE_LIMIT_ERROR_MESSAGE,
            status_code=429,
        )
