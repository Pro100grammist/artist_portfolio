"""
Tests to verify that order pages cannot be accessed by another user using someone else's ID.  
For unauthorized users checking that guests can only access their own orders.
"""

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Order


class OrderAccessControlTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", password="pass12345")
        self.user2 = User.objects.create_user(username="user2", password="pass12345")

        self.user1_order = Order.objects.create(user=self.user1, total_price=100)
        self.user2_order = Order.objects.create(user=self.user2, total_price=150)

    def test_owner_can_access_checkout(self):
        self.client.login(username="user1", password="pass12345")
        response = self.client.get(
            reverse("orders:order-checkout", args=[self.user1_order.id])
        )
        self.assertEqual(response.status_code, 200)

    def test_other_user_cannot_access_checkout(self):
        self.client.login(username="user2", password="pass12345")
        response = self.client.get(
            reverse("orders:order-checkout", args=[self.user1_order.id])
        )
        self.assertEqual(response.status_code, 404)

    def test_owner_can_access_success(self):
        self.client.login(username="user1", password="pass12345")
        response = self.client.get(
            reverse("orders:order-success", args=[self.user1_order.id])
        )
        self.assertEqual(response.status_code, 200)

    def test_other_user_cannot_access_success(self):
        self.client.login(username="user2", password="pass12345")
        response = self.client.get(
            reverse("orders:order-success", args=[self.user1_order.id])
        )
        self.assertEqual(response.status_code, 404)


class GuestOrderAccessControlTests(TestCase):
    def test_guest_can_access_only_same_session_order(self):
        # same session guest
        session = self.client.session
        if not session.session_key:
            session.save()
        session_key = session.session_key

        guest_order = Order.objects.create(session_key=session_key, total_price=50)

        response_ok = self.client.get(
            reverse("orders:order-checkout", args=[guest_order.id])
        )
        self.assertEqual(response_ok.status_code, 200)

        # other session guest
        other_client = self.client_class()
        response_forbidden = other_client.get(
            reverse("orders:order-checkout", args=[guest_order.id])
        )
        self.assertEqual(response_forbidden.status_code, 404)
