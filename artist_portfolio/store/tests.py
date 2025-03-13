from django.test import TestCase
from rest_framework.test import APIClient
from .models import Product, Category


class ProductAPITestCase(TestCase):
    def setUp(self):
        # Створення тестових даних
        self.category = Category.objects.create(name="Paintings")
        self.product1 = Product.objects.create(
            name="Abstract Art",
            description="Beautiful abstract painting.",
            price=100.00,
            size="medium",
            technique="oil",
            paints="blue",
            plot="abstract",
            category=self.category,
        )
        self.product2 = Product.objects.create(
            name="Landscape",
            description="A serene landscape painting.",
            price=150.00,
            size="large",
            technique="acrylic",
            paints="green",
            plot="landscape",
            category=self.category,
        )
        self.client = APIClient()

    def test_product_list(self):
        response = self.client.get('/store/products/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 2)

    def test_filter_by_size(self):
        response = self.client.get('/store/products/?size=medium')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], "Abstract Art")

    def test_search(self):
        response = self.client.get('/store/products/?search=landscape')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], "Landscape")

    def test_pagination(self):
        # Додавання ще одного продукту для перевірки пагінації
        Product.objects.create(
            name="Still Life",
            description="A beautiful still life painting.",
            price=200.00,
            size="small",
            technique="watercolor",
            paints="red",
            plot="still life",
            category=self.category,
        )
        response = self.client.get('/store/products/?page=1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 2)  # 2 продукти на першій сторінці


def test_sorting_by_price(self):
    response = self.client.get('/store/products/?ordering=price')
    self.assertEqual(response.status_code, 200)
    prices = [product['price'] for product in response.data['results']]
    self.assertEqual(prices, sorted(prices))
