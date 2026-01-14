# apps/products/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Товары
    path('', views.ProductListView.as_view(), name='product-list'),
    path('<uuid:pk>/', views.ProductDetailView.as_view(), name='product-detail'),

    # Категории
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/<uuid:pk>/', views.CategoryDetailView.as_view(), name='category-detail'),

    # Тестовый endpoint для RBAC
    path('test-rbac/', views.TestRBACView.as_view(), name='test-rbac'),
]