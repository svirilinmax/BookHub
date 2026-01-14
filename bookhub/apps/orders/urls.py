# apps/orders/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartViewSet, OrderViewSet, ReviewViewSet

router = DefaultRouter()
router.register(r'cart/items', CartViewSet, basename='cartitem')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = [
    path('', include(router.urls)),
]