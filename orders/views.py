from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .selectors import order_list_for_user
from .serializers import CreateOrderSerializer, OrderSerializer
from .services import checkout_cart


class OrderViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return order_list_for_user(self.request.user)

    @action(detail=False, methods=["post"])
    def checkout(self, request):
        serializer = CreateOrderSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        order = checkout_cart(request.user)
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
