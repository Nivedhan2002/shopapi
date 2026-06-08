from .models import Cart


def get_user_cart(user):
    cart, _ = Cart.objects.prefetch_related("items__product__category").get_or_create(user=user)
    return cart
