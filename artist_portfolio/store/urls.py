from django.urls import path
from .views import ProductListView, cart_view

app_name = "store"

urlpatterns = [
    path('', ProductListView.as_view(), name='store-home'),
    path('products/', ProductListView.as_view(), name='product-list'),
]
