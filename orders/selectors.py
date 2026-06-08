from .models import Order


def order_list_for_user(user):
    return (
        Order.objects.filter(user=user)
        .prefetch_related("items")
        .select_related("user")
        .order_by("-created_at")
    )
