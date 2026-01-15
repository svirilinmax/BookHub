from django.contrib import admin

from .models import AccessRule, BusinessElement, Role, UserRole


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """Управление ролями"""

    list_display = ("name", "description")
    list_filter = ("name",)
    search_fields = ("name", "description")
    ordering = ("name",)


@admin.register(BusinessElement)
class BusinessElementAdmin(admin.ModelAdmin):
    """Управление бизнес-элементов"""

    list_display = ("name", "description")
    list_filter = ("name",)
    search_fields = ("name", "description")
    ordering = ("name",)


@admin.register(AccessRule)
class AccessRuleAdmin(admin.ModelAdmin):
    """Управление правил доступа"""

    list_display = (
        "role",
        "element",
        "read_permission",
        "create_permission",
        "update_permission",
        "delete_permission",
    )
    list_filter = ("role", "element")
    search_fields = ("role__name", "element__name")
    ordering = ("role", "element")

    fieldsets = (
        ("Основное", {"fields": ("role", "element")}),
        (
            "Разрешения на чтение",
            {"fields": ("read_permission", "read_all_permission")},
        ),
        ("Разрешения на создание", {"fields": ("create_permission",)}),
        (
            "Разрешения на редактирование",
            {"fields": ("update_permission", "update_all_permission")},
        ),
        (
            "Разрешения на удаление",
            {"fields": ("delete_permission", "delete_all_permission")},
        ),
    )


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    """Управление связи пользователей с ролями"""

    list_display = ("user", "role", "created_at")
    list_filter = ("role", "created_at")
    search_fields = ("user__email", "user__username", "role__name")
    ordering = ("-created_at",)
    autocomplete_fields = ("user", "role")
