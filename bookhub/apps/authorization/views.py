from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import AccessRule, BusinessElement, Role
from .permissions import IsAdmin
from .serializers import (
    AccessRuleDetailSerializer,
    AccessRuleSerializer,
    BusinessElementSerializer,
    RoleSerializer,
)


class AdminRoleViewSet(viewsets.ModelViewSet):
    """
    API для управления ролями (только для администраторов)
    """

    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        return Role.objects.all().order_by("name")


class AdminBusinessElementViewSet(viewsets.ModelViewSet):
    """
    API для управления бизнес-элементами (только для администраторов)
    """

    queryset = BusinessElement.objects.all()
    serializer_class = BusinessElementSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        return BusinessElement.objects.all().order_by("name")


class AdminAccessRuleViewSet(viewsets.ModelViewSet):
    """
    API для управления правилами доступа (только для администраторов)
    """

    queryset = AccessRule.objects.all()
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return AccessRuleDetailSerializer
        return AccessRuleSerializer

    def get_queryset(self):
        return AccessRule.objects.select_related("role", "element").order_by(
            "role__name", "element__name"
        )

    @action(detail=False, methods=["get"])
    def summary(self, request):
        """
        Получить сводку по правам
        """

        summary_data = {}

        roles = Role.objects.all()
        elements = BusinessElement.objects.all()

        for role in roles:
            summary_data[role.name] = {}
            for element in elements:
                try:
                    rule = AccessRule.objects.get(role=role, element=element)
                    summary_data[role.name][element.name] = {
                        "read": rule.read_permission,
                        "create": rule.create_permission,
                        "update": rule.update_permission,
                        "delete": rule.delete_permission,
                        "read_all": rule.read_all_permission,
                        "update_all": rule.update_all_permission,
                        "delete_all": rule.delete_all_permission,
                    }
                except AccessRule.DoesNotExist:
                    summary_data[role.name][element.name] = None

        return Response(summary_data)
