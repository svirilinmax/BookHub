from apps.authorization.permissions import PublicReadOnly, RBACPermission
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


class ProductListView(generics.ListCreateAPIView):
    """
    Список товаров (публичный GET, создание - по правам)
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        """
        GET - публичный доступ
        POST - проверка прав через RBAC
        """
        if self.request.method == "GET":
            return [PublicReadOnly()]
        else:
            return [RBACPermission(element_name="product")]


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Детальный просмотр товара
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        """
        GET - публичный доступ
        PUT/PATCH/DELETE - проверка прав через RBAC
        """
        if self.request.method == "GET":
            return [PublicReadOnly()]
        else:
            return [RBACPermission(element_name="product")]


class CategoryListView(generics.ListCreateAPIView):
    """
    Список категорий
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [PublicReadOnly()]
        else:
            return [RBACPermission(element_name="category")]


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Детальный просмотр категории
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [PublicReadOnly()]
        else:
            return [RBACPermission(element_name="category")]


class TestRBACView(APIView):
    """
    Тестовый endpoint для демонстрации работы RBAC
    """

    def get_permissions(self):
        return [RBACPermission(element_name="product")]

    def get(self, request):
        return Response(
            {
                "message": "GET request successful",
                "user": request.user.email
                if request.user.is_authenticated
                else "Anonymous",
                "has_read_permission": True,
            }
        )

    def post(self, request):
        return Response(
            {
                "message": "POST request successful (requires create permission)",
                "user": request.user.email,
                "has_create_permission": True,
            }
        )
