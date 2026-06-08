from .models import Category, Product


def category_list():
    return Category.objects.all()


def product_list_for_user(user):
    queryset = Product.objects.select_related("category")
    if not (user and user.is_staff):
        queryset = queryset.filter(is_active=True)
    return queryset
