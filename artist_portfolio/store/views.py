from django.shortcuts import render
from django.views.generic.list import ListView
from django_filters.views import FilterView

from .models import Product, Category
from .filters import ProductFilter


class ProductListView(FilterView, ListView):
    """
    Presentation of a list of products with the ability to filter and paginate.
    Inherits from FilterView to support filtering and ListView to display a list of products.
    """
    model = Product
    template_name = 'store/store.html'
    context_object_name = 'products'
    paginate_by = 12  # Number of products per page
    filterset_class = ProductFilter  # A set of filters for products

    def get_queryset(self):
        """
        Returns a filtered and sorted list of products.
        """
        # Getting a QuerySet through a parent class
        queryset = super().get_queryset()
        queryset = queryset.select_related("category")

        # Additional sorting if the `sort` parameter is present
        sort = self.request.GET.get('sort')
        if sort == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort == 'name':
            queryset = queryset.order_by('name')

        return queryset

    def get_context_data(self, **kwargs):
        """
        Adds a list of categories to the template context.
        """
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.prefetch_related("product_set").all()
        return context


def cart_view(request):
    """
    Displays the shopping cart page.
    """
    return render(request, 'store/cart.html', {})


def payment_and_delivery(request):
    return render(request, "store/payment_and_delivery.html")


def exchange_and_refunds(request):
    return render(request, "store/exchange_and_refunds.html")


def privacy_policy(request):
    return render(request, "store/privacy_policy.html")


def user_agreement(request):
    return render(request, "store/user_agreement.html")
