from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models

from store.models import Product


class Order(models.Model):
    """
    An order model that stores information about the customer, status, payment, and delivery.
    """
    STATUS_AWAITING_PAYMENT = "AwaitingPayment"
    STATUS_PENDING = "Pending"
    STATUS_PAID = "Paid"
    STATUS_PROCESSING = "Processing"
    STATUS_SHIPPED = "Shipped"
    STATUS_COMPLETED = "Completed"
    STATUS_CANCELLED = "Cancelled"
    STATUS_REFUNDED = "Refunded"

    STATUS_CHOICES = [
        (STATUS_AWAITING_PAYMENT, "Awaiting Payment"),
        (STATUS_PENDING, "Pending"),
        (STATUS_PAID, "Paid"),
        (STATUS_PROCESSING, "Processing"),
        (STATUS_SHIPPED, "Shipped"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CANCELLED, "Cancelled"),
        (STATUS_REFUNDED, "Refunded"),
    ]

    # Binding to a registered user
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_AWAITING_PAYMENT
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
        if self.user:
            return f"Order {self.id} by {self.user.username}"
        return f"Order {self.id} (Guest)"

    @property
    def active_payment(self):
        active = self.payments.filter(is_active=True).order_by("-created_at").first()
        if active:
            return active
        return self.payments.order_by("-created_at").first()

    def clean(self):
        super().clean()

        if self.pk is None:
            return

        if self.status == self.STATUS_PAID and not self.payments.filter(
            status=OrderPayment.STATUS_PAID
        ).exists():
            raise ValidationError(
                {
                    "status": "Only a verified payment webhook can mark an order as paid."
                }
            )

        if self.status == self.STATUS_REFUNDED and not self.payments.filter(
            status=OrderPayment.STATUS_REFUNDED
        ).exists():
            raise ValidationError(
                {
                    "status": "A verified refund webhook is required before marking an order as refunded."
                }
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


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


class OrderPayment(models.Model):
    """
    Tracks the lifecycle of a provider-backed payment attempt for an order.
    """

    PROVIDER_STRIPE = "stripe"
    PROVIDER_CHOICES = [
        (PROVIDER_STRIPE, "Stripe"),
    ]

    STATUS_CREATED = "created"
    STATUS_PENDING = "pending"
    STATUS_PAID = "paid"
    STATUS_FAILED = "failed"
    STATUS_CANCELED = "canceled"
    STATUS_REFUNDED = "refunded"
    STATUS_CHOICES = [
        (STATUS_CREATED, "Created"),
        (STATUS_PENDING, "Pending"),
        (STATUS_PAID, "Paid"),
        (STATUS_FAILED, "Failed"),
        (STATUS_CANCELED, "Canceled"),
        (STATUS_REFUNDED, "Refunded"),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments")
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES, default=PROVIDER_STRIPE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10)
    attempt_number = models.PositiveIntegerField(default=1)
    idempotency_key = models.CharField(max_length=128, unique=True)
    provider_checkout_session_id = models.CharField(
        max_length=255, blank=True, null=True, unique=True
    )
    provider_payment_intent_id = models.CharField(
        max_length=255, blank=True, null=True, unique=True
    )
    checkout_url = models.URLField(max_length=500, blank=True, null=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_CREATED
    )
    raw_last_event = models.JSONField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["order", "provider", "attempt_number"],
                name="uniq_order_provider_attempt",
            )
        ]

    def __str__(self):
        return f"{self.provider} payment for order {self.order_id} ({self.status})"


class PaymentEvent(models.Model):
    """
    Provider webhook event log used for auditability and idempotent processing.
    """

    provider = models.CharField(max_length=20)
    provider_event_id = models.CharField(max_length=255)
    event_type = models.CharField(max_length=255)
    payload_hash = models.CharField(max_length=64)
    raw_payload = models.TextField(blank=True)
    processed = models.BooleanField(default=False)
    processing_error = models.TextField(blank=True)
    processed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "provider_event_id"],
                name="uniq_provider_event_id",
            )
        ]

    def __str__(self):
        return f"{self.provider}:{self.event_type} ({self.provider_event_id})"
