from django.core.mail import send_mail
from django.conf import settings
from celery import shared_task


@shared_task
def send_order_confirmation_email(order_id):
    from .models import Order

    order = Order.objects.select_related("user").get(pk=order_id)
    send_mail(
        subject=f"Order #{order.id} confirmation",
        message=f"Your order #{order.id} has been received. Total: {order.total_amount}.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.user.email],
        fail_silently=True,
    )
    return f"confirmation-email-sent:{order_id}"


@shared_task
def generate_invoice_pdf(order_id):
    from .models import Order

    order = Order.objects.prefetch_related("items").get(pk=order_id)
    invoice_lines = [
        f"Invoice for order #{order.id}",
        f"Customer: {order.user_id}",
        f"Total: {order.total_amount}",
    ]
    invoice_lines.extend(f"{item.product_name} x {item.quantity}: {item.subtotal}" for item in order.items.all())
    return "\n".join(invoice_lines)
