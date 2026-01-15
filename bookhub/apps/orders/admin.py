from django.contrib import admin

from .models import Cart, CartItem, Order, OrderItem, Review


class OrderItemInline(admin.TabularInline):
    """
    Инлайн для элементов заказа
    """

    model = OrderItem
    extra = 1
    autocomplete_fields = ("product",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Управление заказами
    """

    list_display = ("id_display", "customer", "status", "total_amount", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("customer__email", "customer__username", "shipping_address")
    list_editable = ("status",)
    ordering = ("-created_at",)
    inlines = (OrderItemInline,)
    autocomplete_fields = ("customer",)

    def id_display(self, obj):
        """
        Короткое отображение UUID
        """
        return f"Заказ #{obj.id.hex[:8]}"

    id_display.short_description = "Номер заказа"


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """
    Управление корзиной
    """

    list_display = ("user", "created_at")
    search_fields = ("user__email", "user__username")
    ordering = ("-created_at",)
    autocomplete_fields = ("user",)


class CartItemInline(admin.TabularInline):
    """
    Инлайн для элементов корзины
    """

    model = CartItem
    extra = 1
    autocomplete_fields = ("product",)


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """
    Управление элементами корзины
    """

    list_display = ("cart", "product", "quantity", "created_at")
    list_filter = ("created_at",)
    search_fields = ("cart__user__email", "product__title")
    autocomplete_fields = ("cart", "product")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """
    Управление отзывами
    """

    list_display = ("product", "user", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("product__title", "user__email", "text")
    ordering = ("-created_at",)
    autocomplete_fields = ("product", "user")
