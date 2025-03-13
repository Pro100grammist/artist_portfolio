from django.urls import path
from . import views

app_name = "cart"

urlpatterns = [
    path('', views.cart_view, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<int:product_id>/', views.remove_from_cart, name='remove-from-cart'),
    path('clear-cart/', views.clear_cart, name='clear-cart'),
    path('count/', views.cart_count, name='cart-count'),
    path('make-order/', views.make_order, name='make-order'), 
]
