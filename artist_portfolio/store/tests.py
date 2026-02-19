from django.test import TestCase
from django.urls import reverse

from .models import Product, Category


class ProductListViewTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Paintings")
        Product.objects.create(
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
        Product.objects.create(
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

    def test_product_list_status_and_template(self):
        response = self.client.get(reverse("store:product-list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "store/store.html")
        self.assertContains(response, "Abstract Art")
        self.assertContains(response, "Landscape")

    def test_filter_by_size(self):
        response = self.client.get(reverse("store:product-list"), {"size": "Medium"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Abstract Art")
        self.assertNotContains(response, "Landscape")

    def test_sort_by_price_asc(self):
        response = self.client.get(reverse("store:product-list"), {"sort": "price_asc"})
        self.assertEqual(response.status_code, 200)
        products = list(response.context["products"])
        self.assertEqual(products[0].name, "Abstract Art")
        self.assertEqual(products[1].name, "Landscape")
