# apps/authorization/permissions.py - ИСПРАВЛЕННАЯ ВЕРСИЯ
"""
Кастомные permission классы для RBAC системы BookHub - ИСПРАВЛЕННАЯ ВЕРСИЯ
"""
import logging
from rest_framework import permissions
from django.contrib.auth import get_user_model
from .models import Role, AccessRule, BusinessElement, UserRole

logger = logging.getLogger(__name__)
User = get_user_model()


class RBACPermission(permissions.BasePermission):
    """
    Базовый permission класс для проверки прав через RBAC систему
    """

    # Маппинг HTTP методов к типам прав
    METHOD_TO_PERMISSION = {
        'GET': 'read',
        'OPTIONS': 'read',
        'HEAD': 'read',
        'POST': 'create',
        'PUT': 'update',
        'PATCH': 'update',
        'DELETE': 'delete',
    }

    def __init__(self, element_name=None, require_all=False):
        """
        :param element_name: имя бизнес-элемента (product, order, etc.)
        :param require_all: требует ли право на все объекты (read_all, update_all)
        """
        self.element_name = element_name
        self.require_all = require_all

    def has_permission(self, request, view):
        # Безопасное логирование пути
        try:
            path = getattr(request, 'path', 'unknown_path')
            logger.debug(f"RBACPermission.has_permission called for {request.method} {path}")
        except:
            logger.debug(f"RBACPermission.has_permission called for {request.method}")

        # Публичные маршруты
        if request.method == 'GET' and getattr(view, 'public_read', False):
            logger.debug("Public read route, allowing access")
            return True

        # Анонимные пользователи
        if not request.user or not request.user.is_authenticated:
            logger.warning("User not authenticated")
            return False

        # Администраторы имеют полный доступ
        if request.user.is_staff or request.user.is_superuser:
            logger.debug("User is staff/superuser, allowing access")
            return True

        # Получаем имя элемента из view или параметра
        element_name = getattr(view, 'business_element_name', self.element_name)
        if not element_name:
            # Если имя элемента не указано, используем имя view
            element_name = view.__class__.__name__.lower().replace('view', '').replace('api', '')
            logger.warning(f"No business_element_name found, using derived name: {element_name}")

        logger.debug(f"Checking permissions for element: {element_name}, user: {request.user.email}")

        # Определяем тип права
        permission_type = self._get_permission_type(request.method)
        logger.debug(f"Permission type: {permission_type}")

        # Проверяем право через RBAC
        return self._check_rbac_permission(request.user, element_name, permission_type, request, view)

    def has_object_permission(self, request, view, obj):
        """
        Проверка права на конкретный объект
        """
        logger.debug(f"RBACPermission.has_object_permission called for obj: {obj}")

        if not request.user or not request.user.is_authenticated:
            logger.warning("User not authenticated in object permission")
            return False

        # Администраторы имеют доступ ко всему
        if request.user.is_staff or request.user.is_superuser:
            logger.debug("User is staff/superuser, allowing access")
            return True

        # Получаем имя элемента
        element_name = getattr(view, 'business_element_name', self.element_name)
        if not element_name:
            element_name = type(obj).__name__.lower()
            logger.warning(f"No business_element_name found, using object type: {element_name}")

        # Определяем тип права
        permission_type = self._get_permission_type(request.method)

        # Получаем владельца объекта
        obj_owner = self._get_object_owner(obj)
        logger.debug(f"Object owner: {obj_owner}, Current user: {request.user}")

        # Проверяем через RBAC
        has_permission = self._check_rbac_permission(
            request.user, element_name, permission_type, request, view, obj_owner
        )

        logger.debug(f"Object permission result: {has_permission}")
        return has_permission

    def _get_permission_type(self, http_method):
        """Определяет тип права по HTTP методу"""
        return self.METHOD_TO_PERMISSION.get(http_method, 'read')

    def _get_object_owner(self, obj):
        """Получает владельца объекта"""
        if hasattr(obj, 'user'):
            return obj.user
        elif hasattr(obj, 'owner'):
            return obj.owner
        elif hasattr(obj, 'customer'):
            return obj.customer
        elif hasattr(obj, 'user_id'):
            return obj.user_id
        return None

    def _check_rbac_permission(self, user, element_name, permission_type, request, view, obj_owner=None):
        """
        Основная логика проверки прав через RBAC
        """
        try:
            logger.info(f"_check_rbac_permission: user={user.email}, element={element_name}, "
                       f"permission_type={permission_type}, obj_owner={obj_owner}")

            # Получаем элемент
            element = BusinessElement.objects.get(name=element_name)
            logger.debug(f"BusinessElement found: {element.name}")

            # Получаем роли пользователя через связующую таблицу UserRole
            user_roles = Role.objects.filter(user_roles__user=user).distinct()
            role_names = [role.name for role in user_roles]
            logger.debug(f"User roles: {role_names}")

            # Если у пользователя нет ролей и он не админ, даем роль "guest" по умолчанию
            if not user_roles.exists() and not user.is_staff and not user.is_superuser:
                try:
                    guest_role = Role.objects.get(name='guest')
                    user_roles = [guest_role]
                    logger.debug(f"Assigning default guest role to user")
                except Role.DoesNotExist:
                    logger.error("Guest role does not exist")
                    return False

            # Собираем результаты для всех ролей
            permission_results = []

            # Проверяем права для каждой роли
            for role in user_roles:
                try:
                    access_rule = AccessRule.objects.get(role=role, element=element)
                    logger.debug(f"AccessRule found for role {role.name}: "
                               f"read={access_rule.read_permission}, "
                               f"create={access_rule.create_permission}, "
                               f"update={access_rule.update_permission}, "
                               f"delete={access_rule.delete_permission}")

                    # Проверяем конкретное право
                    if permission_type == 'read':
                        if self.require_all or (hasattr(view, 'action') and view.action in ['list', 'my_cart']):
                            result = access_rule.read_all_permission
                            logger.debug(f"Checking read_all_permission for {role.name}: {result}")
                            permission_results.append(result)
                        else:
                            result = access_rule.read_permission
                            logger.debug(f"Checking read_permission for {role.name}: {result}")
                            permission_results.append(result)

                    elif permission_type == 'create':
                        result = access_rule.create_permission
                        logger.debug(f"Checking create_permission for {role.name}: {result}")
                        permission_results.append(result)

                    elif permission_type == 'update':
                        if self.require_all or (obj_owner and obj_owner != user):
                            result = access_rule.update_all_permission
                            logger.debug(f"Checking update_all_permission for {role.name}: {result}")
                            permission_results.append(result)
                        else:
                            result = access_rule.update_permission
                            logger.debug(f"Checking update_permission for {role.name}: {result}")
                            permission_results.append(result)

                    elif permission_type == 'delete':
                        if self.require_all or (obj_owner and obj_owner != user):
                            result = access_rule.delete_all_permission
                            logger.debug(f"Checking delete_all_permission for {role.name}: {result}")
                            permission_results.append(result)
                        else:
                            result = access_rule.delete_permission
                            logger.debug(f"Checking delete_permission for {role.name}: {result}")
                            permission_results.append(result)

                except AccessRule.DoesNotExist:
                    logger.warning(f"No AccessRule found for role {role.name} and element {element.name}")
                    permission_results.append(False)
                    continue

            # Если у пользователя несколько ролей, достаточно одной из них
            # Например, менеджер имеет обе роли: manager и customer
            if permission_results:
                # Если хотя бы одна роль дает разрешение, возвращаем True
                final_result = any(permission_results)
                logger.info(f"Permission check result for {user.email}: {final_result} "
                           f"(results from roles: {permission_results})")
                return final_result
            else:
                logger.warning("No AccessRules found for any user role")
                return False

        except BusinessElement.DoesNotExist:
            # Если элемент не найден, логируем ошибку
            logger.error(f"BusinessElement '{element_name}' does not exist")
            return False
        except Exception as e:
            logger.error(f"Error in _check_rbac_permission: {str(e)}", exc_info=True)
            return False


# Упрощенные permission классы для быстрого использования
class IsAdmin(RBACPermission):
    """Только для администраторов"""

    def has_permission(self, request, view):
        return request.user and (request.user.is_staff or request.user.is_superuser)


class IsManager(RBACPermission):
    """Для менеджеров и администраторов"""

    def has_permission(self, request, view):
        if request.user and (request.user.is_staff or request.user.is_superuser):
            return True

        # Проверка роли manager через UserRole
        if request.user and request.user.is_authenticated:
            return UserRole.objects.filter(user=request.user, role__name='manager').exists()
        return False


class IsCustomer(RBACPermission):
    """Только для покупателей"""

    def has_permission(self, request, view):
        if request.user and (request.user.is_staff or request.user.is_superuser):
            return False  # Админы не покупатели

        # Проверка роли customer через UserRole
        if request.user and request.user.is_authenticated:
            return UserRole.objects.filter(user=request.user, role__name='customer').exists()
        return False


class PublicReadOnly(permissions.BasePermission):
    """GET запросы доступны всем"""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated


class IsOwnerOrAdmin(permissions.BasePermission):
    """Владелец объекта или администратор"""

    def has_object_permission(self, request, view, obj):
        # Администратор
        if request.user and (request.user.is_staff or request.user.is_superuser):
            return True

        # Владелец
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
        elif hasattr(obj, 'customer'):
            return obj.customer == request.user

        return False