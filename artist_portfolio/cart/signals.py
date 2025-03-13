from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import Cart, CartItem


@receiver(user_logged_in)
def merge_carts(sender, request, user, **kwargs):
    """Merges the session cart with the user's cart after authorization."""

    # Get the shopping cart linked to the current session
    session_cart = Cart.objects.filter(session_key=request.session.session_key).first()

    # Get or create a cart for an authorized user
    user_cart, created = Cart.objects.get_or_create(user=user)

    # If there is a session cart, and it does not match the user's cart,
    # transfer all items from the session cart to the authorized user's cart

    if session_cart and session_cart != user_cart:
        for item in session_cart.items.all():
            user_item, item_created = CartItem.objects.get_or_create(
                cart=user_cart,
                product=item.product,
                defaults={'quantity': item.quantity}
            )
            if not item_created:
                user_item.quantity += item.quantity
                user_item.save()
        session_cart.delete()
