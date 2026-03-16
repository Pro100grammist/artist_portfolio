from django.contrib import admin
from .models import Order, OrderItem, OrderPayment, PaymentEvent


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "total_price", "created_at")
    list_filter = ("status", "payment_method", "shipping_carrier")
    search_fields = ("id", "user__username", "receiver_name", "receiver_phone")


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "quantity", "price")


@admin.register(OrderPayment)
class OrderPaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "provider",
        "status",
        "amount",
        "currency",
        "attempt_number",
        "is_active",
        "paid_at",
        "updated_at",
    )
    list_filter = ("provider", "status", "currency", "is_active")
    search_fields = (
        "order__id",
        "provider_checkout_session_id",
        "provider_payment_intent_id",
        "idempotency_key",
    )
    readonly_fields = ("created_at", "updated_at", "paid_at", "raw_last_event")


@admin.register(PaymentEvent)
class PaymentEventAdmin(admin.ModelAdmin):
    list_display = (
        "provider",
        "provider_event_id",
        "event_type",
        "processed",
        "processed_at",
        "created_at",
    )
    list_filter = ("provider", "event_type", "processed")
    search_fields = ("provider_event_id", "event_type", "payload_hash")
    readonly_fields = (
        "provider",
        "provider_event_id",
        "event_type",
        "payload_hash",
        "raw_payload",
        "processing_error",
        "processed",
        "processed_at",
        "created_at",
    )
