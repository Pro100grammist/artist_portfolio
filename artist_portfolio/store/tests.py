from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from .models import Product, Category, WishlistItem



class ProductListViewTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Paintings")

        self.p1 = Product.objects.create(
            name="Abstract Art",
            description="Beautiful abstract painting.",
            price=100.00,
            size="Medium",
            technique="Oil",
            paints="Blue",
            plot="Abstract",
            category=self.category,
            is_available=True,
        )
        self.p2 = Product.objects.create(
            name="Landscape",
            description="A serene landscape painting.",
            price=150.00,
            size="Large",
            technique="Acrylic",
            paints="Green",
            plot="Landscape",
            category=self.category,
            is_available=True,
        )

    def test_product_list_page_renders(self):
        response = self.client.get(reverse("store:product-list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "store/store.html")
        self.assertIn("products", response.context)
        self.assertIn("categories", response.context)

    def test_product_detail_page_renders(self):
        response = self.client.get(reverse("store:product-detail", args=[self.p1.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "store/product_detail.html")
        self.assertContains(response, "Abstract Art")

    def test_product_detail_404_for_missing_product(self):
        response = self.client.get(reverse("store:product-detail", args=[999999]))
        self.assertEqual(response.status_code, 404)

    def test_filter_by_size(self):
        response = self.client.get(reverse("store:product-list"), {"size": "Medium"})
        self.assertEqual(response.status_code, 200)

        products = list(response.context["products"])
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].name, "Abstract Art")

    def test_filter_by_category_name(self):
        response = self.client.get(
            reverse("store:product-list"),
            {"category": "Paintings"},
        )
        self.assertEqual(response.status_code, 200)

        products = list(response.context["products"])
        self.assertEqual(len(products), 2)

    def test_sort_by_price_ascending(self):
        response = self.client.get(
            reverse("store:product-list"),
            {"sort": "price_asc"},
        )
        self.assertEqual(response.status_code, 200)

        products = list(response.context["products"])
        self.assertEqual([p.name for p in products], ["Abstract Art", "Landscape"])

    def test_sort_by_price_descending(self):
        response = self.client.get(
            reverse("store:product-list"),
            {"sort": "price_desc"},
        )
        self.assertEqual(response.status_code, 200)

        products = list(response.context["products"])
        self.assertEqual([p.name for p in products], ["Landscape", "Abstract Art"])

    def test_search_by_name(self):
        response = self.client.get(reverse("store:product-list"), {"q": "Abstract"})
        self.assertEqual(response.status_code, 200)
        products = list(response.context["products"])
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].name, "Abstract Art")


class WishlistTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="u1", password="pass12345")
        self.category = Category.objects.create(name="Paintings")
        self.product = Product.objects.create(
            name="Test",
            price=10,
            category=self.category,
            is_available=True,
        )

    def test_toggle_wishlist_add_and_remove(self):
        self.client.login(username="u1", password="pass12345")

        url = reverse("store:toggle-wishlist", args=[self.product.id])

        # add
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            WishlistItem.objects.filter(user=self.user, product=self.product).exists()
        )

        # remove
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            WishlistItem.objects.filter(user=self.user, product=self.product).exists()
        ) 