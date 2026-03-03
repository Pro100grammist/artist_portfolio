from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.list import ListView
from django.views.generic import DetailView
from django_filters.views import FilterView

from .models import Product, Category, WishlistItem
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
        q = self.request.GET.get("q")
        if q:
            queryset = queryset.filter(name__icontains=q)

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
        context['categories'] = Category.objects.all()
        return context


class ProductDetailView(DetailView):
    """
    Presentation of the product details page.
    Inherits from DetailView to display detailed information about a specific product.
    """
    model = Product
    template_name = 'store/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        """
        Adds additional information about the product to the template context.
        """
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
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


@login_required
def toggle_wishlist(request, product_id):
    if request.method != "POST":
        return redirect("store:product-detail", pk=product_id)

    product = get_object_or_404(Product, id=product_id)
    item, created = WishlistItem.objects.get_or_create(
        user=request.user, product=product
    )
    if not created:
        item.delete()

    return redirect("store:product-detail", pk=product_id)


@login_required
def wishlist_page(request):
    items = (
        WishlistItem.objects.filter(user=request.user)
        .select_related("product")
    )
    return render(request, "store/wishlist.html", {"wishlist_items": items})