from django.contrib import admin
from django.utils.html import format_html
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('product', 'quantity')


class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'updated_at')
    search_fields = ('user__username',)
    readonly_fields = ('created_at', 'updated_at')
    list_filter = ('created_at',)
    inlines = [CartItemInline]

    def user_link(self, obj):
        if obj.user:
            return format_html('<a href="/admin/auth/user/{}/change/">{}</a>', obj.user.id, obj.user.username)
        return 'Anonymous'

    user_link.short_description = 'User'

    def is_anonymous(self, obj):
        return obj.user is None

    is_anonymous.boolean = True
    is_anonymous.short_description = 'Anonymous basket'


admin.site.register(Cart, CartAdmin)
