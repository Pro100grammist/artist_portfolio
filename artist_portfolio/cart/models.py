from django.apps import apps
from django.db import models
from django.contrib.auth.models import User


class Cart(models.Model):
    """
    Represents a shopping cart, which can be associated with either an authenticated user
    or an anonymous session (via session_key).
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="The user who owns the cart. Can be null for anonymous users.",
    )
    session_key = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        unique=True,
        help_text="A unique session identifier for guests without an account.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="The timestamp when the cart was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="The timestamp when the cart was last updated."
    )

    def __str__(self):
        return f"Cart ({self.id}) - User: {self.user} | Session: {self.session_key}"

    @property
    def items_count(self):
        """Returns the total number of items in the cart."""
        return self.items.count()

    @property
    def total_price(self):
        """Calculates the total price of all items in the cart."""
        return sum(item.product.price * item.quantity for item in self.items.all())


class CartItem(models.Model):
    """
    Represents an item in the shopping cart, linking a cart with a specific product.
    """

    cart = models.ForeignKey(
        Cart,
        related_name="items",
        on_delete=models.CASCADE,
        db_index=True,
        help_text="The cart that this item belongs to.",
    )
    product = models.ForeignKey(
        "store.Product",
        on_delete=models.CASCADE,
        db_index=True,
        help_text="The product added to the cart.",
    )
    quantity = models.PositiveIntegerField(
        default=1, help_text="The number of units of the product in the cart."
    )

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    @staticmethod
    def get_product_model():
        """Retrieves the Product model dynamically."""
        return apps.get_model("store", "Product")
