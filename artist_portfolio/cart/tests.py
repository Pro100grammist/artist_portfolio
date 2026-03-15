from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from artist_portfolio.security import RATE_LIMIT_ERROR_MESSAGE
from cart.models import Cart, CartItem
from store.models import Category, Product


@override_settings(RATELIMIT_ENABLE=True)
class CartRateLimitTests(TestCase):
    def setUp(self):
        cache.clear()
        self.category = Category.objects.create(name="Paintings")
        self.product = Product.objects.create(
            name="Rate Limited Product",
            price=99.00,
            category=self.category,
            is_available=True,
        )
        session = self.client.session
        if not session.session_key:
            session.save()
        self.session_key = session.session_key

    def tearDown(self):
        cache.clear()

    def _get_cart(self):
        cart, _ = Cart.objects.get_or_create(session_key=self.session_key)
        return cart

    def _ensure_cart_has_item(self):
        cart = self._get_cart()
        CartItem.objects.update_or_create(
            cart=cart,
            product=self.product,
            defaults={"quantity": 1},
        )
        return cart

    def test_add_to_cart_returns_429_after_ten_requests(self):
        url = reverse("cart:add-to-cart", args=[self.product.id])

        for _ in range(10):
            response = self.client.post(
                url,
                HTTP_ACCEPT="application/json",
                HTTP_X_REQUESTED_WITH="XMLHttpRequest",
            )
            self.assertEqual(response.status_code, 200)

        response = self.client.post(
            url,
            HTTP_ACCEPT="application/json",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 429)
        self.assertJSONEqual(
            response.content,
            {"error": RATE_LIMIT_ERROR_MESSAGE},
        )

    def test_remove_from_cart_returns_429_after_ten_requests(self):
        url = reverse("cart:remove-from-cart", args=[self.product.id])

        for _ in range(10):
            self._ensure_cart_has_item()
            response = self.client.post(
                url,
                HTTP_ACCEPT="application/json",
                HTTP_X_REQUESTED_WITH="XMLHttpRequest",
            )
            self.assertEqual(response.status_code, 200)

        self._ensure_cart_has_item()
        response = self.client.post(
            url,
            HTTP_ACCEPT="application/json",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 429)
        self.assertJSONEqual(
            response.content,
            {"error": RATE_LIMIT_ERROR_MESSAGE},
        )

    def test_clear_cart_returns_429_after_ten_requests(self):
        url = reverse("cart:clear-cart")

        for _ in range(10):
            self._ensure_cart_has_item()
            response = self.client.post(
                url,
                HTTP_ACCEPT="application/json",
                HTTP_X_REQUESTED_WITH="XMLHttpRequest",
            )
            self.assertEqual(response.status_code, 200)

        self._ensure_cart_has_item()
        response = self.client.post(
            url,
            HTTP_ACCEPT="application/json",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 429)
        self.assertJSONEqual(
            response.content,
            {"error": RATE_LIMIT_ERROR_MESSAGE},
        )

    def test_make_order_returns_429_after_ten_requests(self):
        url = reverse("cart:make-order")

        for _ in range(10):
            self._ensure_cart_has_item()
            response = self.client.post(url)
            self.assertEqual(response.status_code, 302)

        self._ensure_cart_has_item()
        response = self.client.post(url)

        self.assertEqual(response.status_code, 429)
        self.assertContains(
            response,
            RATE_LIMIT_ERROR_MESSAGE,
            status_code=429,
        )
