from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .selectors import get_user_cart
from .serializers import AddCartItemSerializer, CartItemSerializer, CartSerializer
from .services import add_item_to_cart, clear_cart, remove_cart_item, update_cart_item


class CartViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer

    def list(self, request):
        return Response(self.get_serializer(get_user_cart(request.user)).data)

    @action(detail=False, methods=["post"])
    def add_item(self, request):
        serializer = AddCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = add_item_to_cart(
            user=request.user,
            product=serializer.validated_data["product"],
            quantity=serializer.validated_data["quantity"],
        )
        return Response(CartItemSerializer(item).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["patch"], url_path="items/(?P<item_id>[^/.]+)")
    def update_item(self, request, item_id=None):
        item = update_cart_item(request.user, item_id, request.data, CartItemSerializer)
        return Response(CartItemSerializer(item).data)

    @action(detail=False, methods=["delete"], url_path="items/(?P<item_id>[^/.]+)")
    def remove_item(self, request, item_id=None):
        if not remove_cart_item(request.user, item_id):
            return Response({"detail": "Cart item not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["delete"])
    def clear(self, request):
        clear_cart(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
