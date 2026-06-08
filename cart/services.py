from django.shortcuts import get_object_or_404

from common.exceptions import ServiceError
from .models import CartItem
from .selectors import get_user_cart


def add_item_to_cart(user, product, quantity):
    cart = get_user_cart(user)
    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={"quantity": quantity},
    )
    if not created:
        item.quantity += quantity
    if item.quantity > product.stock:
        raise ServiceError("Requested quantity exceeds available stock")
    item.save()
    return item


def update_cart_item(user, item_id, data, serializer_class):
    cart = get_user_cart(user)
    item = get_object_or_404(cart.items.select_related("product", "product__category"), pk=item_id)
    serializer = serializer_class(item, data=data, partial=True)
    serializer.is_valid(raise_exception=True)
    return serializer.save()


def remove_cart_item(user, item_id):
    deleted, _ = get_user_cart(user).items.filter(pk=item_id).delete()
    return bool(deleted)


def clear_cart(user):
    get_user_cart(user).items.all().delete()
