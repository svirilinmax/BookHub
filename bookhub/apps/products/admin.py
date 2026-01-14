from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Админка для категорий"""
    list_display = ('name', 'slug', 'parent', 'created_at')
    list_filter = ('parent', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Админка для товаров"""
    list_display = ('title', 'author', 'price', 'category', 'is_available', 'stock', 'owner')
    list_filter = ('is_available', 'category', 'created_at')
    search_fields = ('title', 'author', 'description')
    list_editable = ('price', 'is_available', 'stock')
    ordering = ('-created_at',)
    autocomplete_fields = ('category', 'owner')

    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'author', 'description')
        }),
        ('Цена и наличие', {
            'fields': ('price', 'stock', 'is_available')
        }),
        ('Категория и владелец', {
            'fields': ('category', 'owner')
        }),
    )