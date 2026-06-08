from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .selectors import payment_list_for_user
from .serializers import PaymentSerializer, SimulatePaymentSerializer
from .services import simulate_payment


class PaymentViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentSerializer

    def get_queryset(self):
        return payment_list_for_user(self.request.user)

    @action(detail=False, methods=["post"])
    def simulate(self, request):
        serializer = SimulatePaymentSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        payment = simulate_payment(
            order=serializer.validated_data["order"],
            success=serializer.validated_data["success"],
        )
        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)
