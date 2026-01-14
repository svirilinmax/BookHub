# apps/products/serializers.py
from rest_framework import serializers
from .models import Product, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'parent_id', 'created_at']
        read_only_fields = ['id', 'created_at']


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'author', 'description', 'price',
            'category', 'category_name', 'owner', 'stock',
            'is_available', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'owner']

    def create(self, validated_data):
        # Устанавливаем владельца как текущего пользователя
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)