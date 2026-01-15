from apps.products.serializers import ProductSerializer
from rest_framework import serializers

from ..products.models import Product
from .models import Cart, CartItem, Order, OrderItem, Review


class CartItemSerializer(serializers.ModelSerializer):
    """
    Сериализатор для элемента корзины
    """

    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), write_only=True, source="product"
    )

    class Meta:
        model = CartItem
        fields = ["id", "product", "product_id", "quantity", "created_at"]
        read_only_fields = ["id", "created_at", "cart"]

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Количество должно быть не менее 1")
        return value


class CartSerializer(serializers.ModelSerializer):
    """
    Сериализатор для корзины
    """

    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "user", "items", "total_price", "created_at"]
        read_only_fields = ["id", "user", "created_at"]

    def get_total_price(self, obj):
        return sum(item.product.price * item.quantity for item in obj.items.all())


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Сериализатор для элемента заказа
    """

    product = ProductSerializer(read_only=True)
    product_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_id", "quantity", "price", "created_at"]
        read_only_fields = ["id", "price", "created_at"]


class OrderSerializer(serializers.ModelSerializer):
    """
    Сериализатор для заказа
    """

    items = OrderItemSerializer(many=True, read_only=True)
    customer_email = serializers.EmailField(source="customer.email", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "customer",
            "customer_email",
            "status",
            "total_amount",
            "shipping_address",
            "notes",
            "items",
            "created_at",
        ]
        read_only_fields = ["id", "customer", "total_amount", "created_at"]

    def validate_shipping_address(self, value):
        if not value.strip():
            raise serializers.ValidationError("Адрес доставки не может быть пустым")
        return value.strip()


class ReviewSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отзыва
    """

    user_email = serializers.EmailField(source="user.email", read_only=True)
    product_title = serializers.CharField(source="product.title", read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "product",
            "product_title",
            "user",
            "user_email",
            "rating",
            "text",
            "created_at",
        ]
        read_only_fields = ["id", "user", "created_at"]

    def validate(self, data):
        # Проверяем, не оставлял ли пользователь уже отзыв на этот товар
        if self.instance is None:  # Только при создании
            user = self.context["request"].user
            product = data.get("product")
            if Review.objects.filter(user=user, product=product).exists():
                raise serializers.ValidationError(
                    "Вы уже оставляли отзыв на этот товар"
                )
        return data
