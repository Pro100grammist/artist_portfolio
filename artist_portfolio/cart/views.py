from django.shortcuts import redirect, get_object_or_404, render
from django.http import JsonResponse
from django.contrib.sessions.models import Session
from django.db import models
from django.contrib import messages
from store.models import Product
from orders.models import Order, OrderItem
from cart.models import Cart, CartItem


def cart_view(request):
    """
    Renders the cart page with the current user's cart.
    """
    cart = get_or_create_cart(request)
    return render(request, "cart/cart.html", {"cart": cart})


def get_or_create_cart(request):
    """
    Retrieves the cart for the current user or session.
    If no cart exists, a new one is created.
    """
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)
    return cart


def add_to_cart(request, product_id):
    """
    Adds a product to the cart. If the product is already in the cart, increases the quantity.
    Only accepts POST requests.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method. Use POST."}, status=405)

    product = get_object_or_404(Product, id=product_id)
    cart = get_or_create_cart(request)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return JsonResponse({"message": f"{product.name} added to cart."})


def remove_from_cart(request, product_id):
    """
    Removes a product from the cart.
    Only accepts POST requests.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method. Use POST."}, status=405)

    cart = get_or_create_cart(request)
    cart_item = CartItem.objects.filter(cart=cart, product_id=product_id).first()

    if cart_item:
        cart_item.delete()
        total_price = (
            cart.items.aggregate(
                total=models.Sum(models.F("product__price") * models.F("quantity"))
            )["total"]
            or 0
        )
        return JsonResponse(
            {
                "message": "The item has been removed from the cart.",
                "total_price": total_price,
            }
        )

    return JsonResponse({"error": "The item was not found in the cart."}, status=404)


def clear_cart(request):
    """
    Clears all items from the cart.
    Accepts POST requests and supports AJAX.
    """
    if request.method == "POST":
        cart = get_or_create_cart(request)
        cart.items.all().delete()

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"message": "The cart has been cleared."})
        return redirect("store:store-home")

    return JsonResponse({"error": "Invalid request method."}, status=405)


def cart_count(request):
    """
    Returns the total number of items in the cart.
    """
    cart = get_or_create_cart(request)
    count = cart.items.aggregate(total=models.Sum("quantity"))["total"] or 0
    return JsonResponse({"count": count})


def make_order(request):
    """
    Creates an order from the current cart, associates it with a user or session,
    and redirects to the checkout page.
    """
    cart = get_or_create_cart(request)

    if not cart.items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect("cart:cart-view")

    # Create order
    order_data = {"total_price": cart.total_price}
    if request.user.is_authenticated:
        order_data["user"] = request.user
    else:
        order_data["session_key"] = request.session.session_key

    order = Order.objects.create(**order_data)

    # Add cart items to order
    order_items = [
        OrderItem(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price,
        )
        for item in cart.items.all()
    ]
    OrderItem.objects.bulk_create(order_items)

    # Clear cart
    cart.items.all().delete()

    messages.success(request, "Your order has been placed successfully!")
    return redirect("orders:order-checkout", order_id=order.id)
