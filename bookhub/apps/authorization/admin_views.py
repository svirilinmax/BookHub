# apps/authorization/admin_views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Role, BusinessElement, AccessRule
from .serializers import RoleSerializer, BusinessElementSerializer, AccessRuleSerializer
from .permissions import IsAdmin

class RoleViewSet(viewsets.ModelViewSet):
    """Управление ролями (только для админов)"""
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

class BusinessElementViewSet(viewsets.ModelViewSet):
    """Управление бизнес-элементами (только для админов)"""
    queryset = BusinessElement.objects.all()
    serializer_class = BusinessElementSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

class AccessRuleViewSet(viewsets.ModelViewSet):
    """Управление правилами доступа (только для админов)"""
    queryset = AccessRule.objects.all()
    serializer_class = AccessRuleSerializer
    permission_classes = [IsAuthenticated, IsAdmin]