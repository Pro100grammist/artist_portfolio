from django.db import models
from django.contrib.auth.models import User
from store.models import Product


class Order(models.Model):
    """
    An order model that stores information about the customer, status, payment, and delivery.
    """
    STATUS_CHOICES = [
        ("AwaitingPayment", "Awaiting Payment"),
        ("Pending", "Pending"),
        ("Processing", "Processing"),
        ("Shipped", "Shipped"),
        ("Completed", "Completed"),
        ("Cancelled", "Cancelled"),
    ]

    # Binding to a registered user
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="AwaitingPayment"
    )
    # Session ID for guests (unregistered users)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Delivery
    country = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    shipping_carrier = models.CharField(max_length=50, blank=True, null=True)
    tracking_number = models.CharField(
        max_length=50, blank=True, null=True
    )  # Invoice number

    # Payment
    payment_method = models.CharField(max_length=50, blank=True, null=True)

    # Recipient
    receiver_name = models.CharField(max_length=255, blank=True, null=True)
    receiver_phone = models.CharField(max_length=20, blank=True, null=True)

    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"


class OrderItem(models.Model):
    """
    An item in an order that contains information about the product, quantity, and price.
    """

    # Binding to a specific order
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} (x{self.quantity}) in Order {self.order.id}"
