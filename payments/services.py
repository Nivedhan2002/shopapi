import uuid

from django.db import transaction

from orders.models import Order
from orders.tasks import generate_invoice_pdf
from .models import Payment


def simulate_payment(order, success=True):
    with transaction.atomic():
        payment, _ = Payment.objects.select_for_update().get_or_create(
            order=order,
            defaults={"amount": order.total_amount},
        )
        payment.amount = order.total_amount
        payment.status = Payment.Status.SUCCESS if success else Payment.Status.FAILED
        payment.transaction_id = f"sim_{uuid.uuid4().hex}"
        payment.save(update_fields=["amount", "status", "transaction_id", "updated_at"])
        if success:
            order.status = Order.Status.PAID
            order.save(update_fields=["status", "updated_at"])
    if success:
        generate_invoice_pdf.delay(order.id)
    return payment
