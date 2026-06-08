from orders.models import Order
from .models import Payment


def payment_list_for_user(user):
    return Payment.objects.filter(order__user=user).select_related("order")


def pending_orders_for_user(user):
    return Order.objects.filter(user=user, status=Order.Status.PENDING)
