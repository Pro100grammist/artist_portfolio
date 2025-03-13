from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path("checkout/<int:order_id>/", views.order_checkout, name="order-checkout"),
    path("success/<int:order_id>/", views.order_success, name="order-success"),
]
