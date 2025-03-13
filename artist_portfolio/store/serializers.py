from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for the Product model (API)
    """
    category = serializers.StringRelatedField()  # Display a category as a string

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'size',
            'technique', 'paints', 'plot', 'category', 'image'
        ]
