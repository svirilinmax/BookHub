from rest_framework import serializers

from .models import AccessRule, BusinessElement, Role


class RoleSerializer(serializers.ModelSerializer):
    """
    Сериализатор для ролей
    """

    user_count = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = ["id", "name", "description", "user_count", "created_at"]
        read_only_fields = ["id", "created_at"]

    def get_user_count(self, obj):
        return obj.users.count()


class BusinessElementSerializer(serializers.ModelSerializer):
    """
    Сериализатор для бизнес-элементов
    """

    class Meta:
        model = BusinessElement
        fields = ["id", "name", "description", "created_at"]
        read_only_fields = ["id", "created_at"]


class AccessRuleSerializer(serializers.ModelSerializer):
    """
    Сериализатор для правил доступа
    """

    role_name = serializers.CharField(source="role.name", read_only=True)
    element_name = serializers.CharField(source="element.name", read_only=True)

    class Meta:
        model = AccessRule
        fields = [
            "id",
            "role",
            "role_name",
            "element",
            "element_name",
            "read_permission",
            "read_all_permission",
            "create_permission",
            "update_permission",
            "update_all_permission",
            "delete_permission",
            "delete_all_permission",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class AccessRuleDetailSerializer(AccessRuleSerializer):
    """
    Детальный сериализатор для правил доступа
    """

    role = RoleSerializer(read_only=True)
    element = BusinessElementSerializer(read_only=True)
