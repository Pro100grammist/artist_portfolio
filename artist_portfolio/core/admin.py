from django.contrib import admin
from .models import Artwork, ContactMessage


@admin.register(Artwork)
class ArtworkAdmin(admin.ModelAdmin):
    list_display = ("title", "price", "created_at")
    search_fields = ("title", "description")


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "created_at", "is_processed")
    list_filter = ("is_processed", "created_at")
    search_fields = ("name", "email", "message")
    ordering = ("-created_at",)

    def mark_as_processed(self, request, queryset):
        queryset.update(is_processed=True)

    mark_as_processed.short_description = "Mark as processed"

    actions = [mark_as_processed]
