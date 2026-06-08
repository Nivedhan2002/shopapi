from rest_framework import viewsets
from rest_framework.response import Response

from .permissions import IsAdminOrReadOnly
from .selectors import category_list, product_list_for_user
from .serializers import CategorySerializer, ProductSerializer
from .services import get_cached_public_product_response


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = category_list()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "slug"
    search_fields = ("name",)
    ordering_fields = ("name", "created_at")


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ("category", "category__slug", "is_active")
    search_fields = ("name", "description", "category__name")
    ordering_fields = ("price", "created_at", "name")

    def get_queryset(self):
        return product_list_for_user(self.request.user)

    def list(self, request, *args, **kwargs):
        if not request.user.is_staff:
            data = get_cached_public_product_response(
                request,
                producer=lambda: super(ProductViewSet, self).list(request, *args, **kwargs).data,
            )
            return Response(data)
        return super().list(request, *args, **kwargs)
