from django.urls import path
from django.contrib.flatpages.views import flatpage
from .views import (
    ProductListView,
    ProductDetailView,
    cart_view,
    payment_and_delivery,
    exchange_and_refunds,
    privacy_policy,
    user_agreement,
)

app_name = "store"

urlpatterns = [
    path("", ProductListView.as_view(), name="store-home"),
    path("products/", ProductListView.as_view(), name="product-list"),
    path("products/<int:pk>/", ProductDetailView.as_view(), name="product-detail"),
    path("payment-and-delivery/", payment_and_delivery, name="payment-and-delivery"),
    path("exchange-and-refunds/", flatpage, {'url': '/store/exchange-and-refunds/'}, name="exchange-and-refunds"),
    path("privacy-policy/", flatpage, {'url': '/store/privacy-policy/'}, name='privacy-policy'),
    path("user-agreement/", flatpage, {'url': '/store/user-agreement/'}, name='user-agreement'),
]
