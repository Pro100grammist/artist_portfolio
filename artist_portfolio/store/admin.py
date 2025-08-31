from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Category


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'size', 'technique', 'is_available')
    readonly_fields = ("preview",)  # додаємо поле тільки для перегляду

    fieldsets = (
        (None, {
            "fields": (
                "name", "description", "price", "size", "technique",
                "paints", "plot", "category", "image", "is_available", "preview"
            ),
        }),
    )

    def preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 200px; max-width: 200px; border:1px solid #ccc;"/>',
                obj.image.url
            )
        return "(No image uploaded)"

    preview.short_description = "Preview"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
