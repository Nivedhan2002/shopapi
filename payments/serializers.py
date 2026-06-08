from rest_framework import serializers

from orders.models import Order
from .models import Payment
from .selectors import pending_orders_for_user


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ("id", "order", "status", "transaction_id", "amount", "created_at", "updated_at")
        read_only_fields = ("id", "status", "transaction_id", "amount", "created_at", "updated_at")


class SimulatePaymentSerializer(serializers.Serializer):
    order_id = serializers.PrimaryKeyRelatedField(queryset=Order.objects.none(), source="order")
    success = serializers.BooleanField(default=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request:
            self.fields["order_id"].queryset = pending_orders_for_user(request.user)
