import django_filters
from .models import Product, Category


class ProductFilter(django_filters.FilterSet):
    """
    Filter for products by different parameters.
    """
    price_min = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    price_max = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    category = django_filters.CharFilter(field_name="category__name", lookup_expr="icontains")
    size = django_filters.CharFilter(lookup_expr="icontains")
    technique = django_filters.CharFilter(lookup_expr="icontains")
    paints = django_filters.CharFilter(lookup_expr="icontains")
    plot = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Product
        fields = ['category', 'size', 'technique', 'paints', 'plot', 'price_min', 'price_max']
