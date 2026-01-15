from apps.authorization.permissions import IsAdmin, RBACPermission
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import User
from .serializers import UserProfileSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления пользователями
    """

    queryset = User.objects.filter(deleted_at__isnull=True)  # Только не удаленные
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated, RBACPermission]

    # Указываем бизнес-элемент для RBAC
    business_element_name = "user"

    def get_queryset(self):
        user = self.request.user

        # Админы видят всех пользователей
        if user.is_staff:
            return User.objects.filter(deleted_at__isnull=True)

        # Менеджеры видят всех пользователей (но не могут удалять)
        if user.roles.filter(name="manager").exists():
            return User.objects.filter(deleted_at__isnull=True)

        # Обычные пользователи видят только себя
        return User.objects.filter(id=user.id, deleted_at__isnull=True)

    def perform_destroy(self, instance):
        """
        Мягкое удаление пользователя
        """

        instance.deleted_at = timezone.now()
        instance.is_active = False
        instance.save()

    @action(detail=True, methods=["post"], permission_classes=[IsAdmin])
    def restore(self, request, pk=None):
        """
        Восстановить мягко удаленного пользователя (только для админов)
        """

        user = self.get_object()
        if user.deleted_at:
            user.deleted_at = None
            user.is_active = True
            user.save()
            return Response({"status": "Пользователь восстановлен"})
        return Response(
            {"error": "Пользователь не был удален"}, status=status.HTTP_400_BAD_REQUEST
        )
