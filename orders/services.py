from django.db import transaction

from cart.models import Cart
from common.exceptions import ServiceError
from products.models import Product
from .models import Order, OrderItem
from .tasks import send_order_confirmation_email


def validate_cart_for_checkout(cart):
    if not cart or not cart.items.exists():
        raise ServiceError("Cart is empty")
    for item in cart.items.all():
        if item.quantity > item.product.stock:
            raise ServiceError(f"Insufficient stock for {item.product.name}")


def checkout_cart(user):
    cart = Cart.objects.prefetch_related("items__product").filter(user=user).first()
    validate_cart_for_checkout(cart)
    with transaction.atomic():
        order = Order.objects.create(user=user, total_amount=cart.total)
        order_items = []
        product_updates = []
        for cart_item in cart.items.select_related("product"):
            product = cart_item.product
            product.stock -= cart_item.quantity
            product_updates.append(product)
            order_items.append(
                OrderItem(
                    order=order,
                    product=product,
                    product_name=product.name,
                    unit_price=product.price,
                    quantity=cart_item.quantity,
                )
            )
        OrderItem.objects.bulk_create(order_items)
        Product.objects.bulk_update(product_updates, ["stock"])
        cart.items.all().delete()
    send_order_confirmation_email.delay(order.id)
    return order
