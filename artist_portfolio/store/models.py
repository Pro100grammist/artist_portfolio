from django.db import models


class Product(models.Model):
    """
    A model of a product in a store.
    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    size = models.CharField(max_length=50, blank=True, null=True)
    technique = models.CharField(max_length=100, blank=True, null=True)
    paints = models.CharField(max_length=100, blank=True, null=True)
    plot = models.CharField(max_length=100, blank=True, null=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_available = models.BooleanField(default=False)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name


class Category(models.Model):
    """
    Product category model.
    """
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
