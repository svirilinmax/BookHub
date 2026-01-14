# apps/orders/views.py - исправленная версия для корзины
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction

from . import serializers
from .models import Cart, CartItem, Order, OrderItem, Review
from .serializers import (
    CartSerializer, CartItemSerializer,
    OrderSerializer, OrderItemSerializer,
    ReviewSerializer
)
from apps.authorization.permissions import RBACPermission
from apps.products.models import Product


class CartViewSet(viewsets.ModelViewSet):
    """ViewSet для корзины"""
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated, RBACPermission]

    business_element_name = 'cart'

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return CartItem.objects.all()

        cart, _ = Cart.objects.get_or_create(user=user)
        return CartItem.objects.filter(cart=cart)

    def get_cart(self):
        user = self.request.user
        cart, created = Cart.objects.get_or_create(user=user)
        return cart

    def perform_create(self, serializer):
        """Добавляет товар в корзину или обновляет количество"""
        with transaction.atomic():
            cart = self.get_cart()

            # Получаем product из валидированных данных
            product = serializer.validated_data.get('product')
            if not product:
                raise serializers.ValidationError({"product": "Товар обязателен"})

            quantity = serializer.validated_data.get('quantity', 1)

            # Проверяем, есть ли уже такой товар в корзине
            existing_item = CartItem.objects.filter(cart=cart, product=product).first()

            if existing_item:
                # Обновляем количество
                existing_item.quantity += quantity
                existing_item.save()
                serializer.instance = existing_item
            else:
                # Создаем новый элемент
                serializer.save(cart=cart)

    @action(detail=False, methods=['get'])
    def my_cart(self, request):
        """Получить корзину текущего пользователя"""
        cart = self.get_cart()
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def checkout(self, request):
        """Оформить заказ из корзины"""
        cart = self.get_cart()

        if not cart.items.exists():
            return Response(
                {'error': 'Корзина пуста'},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            # Создаем заказ
            order = Order.objects.create(
                customer=request.user,
                shipping_address=request.data.get('shipping_address', ''),
                notes=request.data.get('notes', '')
            )

            # Переносим товары из корзины в заказ
            total_amount = 0
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
                total_amount += cart_item.product.price * cart_item.quantity

            order.total_amount = total_amount
            order.save()

            # Очищаем корзину
            cart.items.all().delete()

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet для заказов"""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, RBACPermission]

    business_element_name = 'order'

    def get_queryset(self):
        user = self.request.user

        # Админы видят все заказы
        if user.is_staff:
            return Order.objects.all()

        # Менеджеры видят все заказы (но не могут удалять)
        if user.roles.filter(name='manager').exists():
            return Order.objects.all()

        # Покупатели видят только свои заказы
        return Order.objects.filter(customer=user)

    def perform_create(self, serializer):
        # При создании заказа автоматически назначаем текущего пользователя
        serializer.save(customer=self.request.user)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Обновить статус заказа (для менеджеров/админов)"""
        order = self.get_object()
        new_status = request.data.get('status')

        if new_status not in dict(Order.STATUS_CHOICES):
            return Response(
                {'error': 'Недопустимый статус'},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = new_status
        order.save()

        return Response({'status': 'Статус обновлен', 'new_status': new_status})


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet для отзывов"""
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    business_element_name = 'review'

    def get_queryset(self):
        user = self.request.user

        # Админы видят все отзывы
        if user.is_staff:
            return Review.objects.all().order_by('-created_at')

        # Покупатели видят все отзывы, но могут редактировать только свои
        return Review.objects.all().order_by('-created_at')

    def perform_create(self, serializer):
        # При создании отзыва автоматически назначаем текущего пользователя
        serializer.save(user=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context