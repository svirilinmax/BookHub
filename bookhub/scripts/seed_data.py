# scripts/seed_data.py
import os
import sys
import django

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookhub.settings')
django.setup()

from apps.authorization.models import Role, BusinessElement, AccessRule
from apps.users.models import User


def create_roles():
    """Создаем базовые роли"""
    roles_data = [
        ('admin', 'Администратор системы. Полный доступ ко всем функциям.'),
        ('manager', 'Менеджер магазина. Управление товарами и заказами.'),
        ('customer', 'Покупатель. Может делать заказы и оставлять отзывы.'),
        ('guest', 'Гость. Только просмотр товаров.')
    ]

    for name, description in roles_data:
        Role.objects.get_or_create(
            name=name,
            defaults={'description': description}
        )
    print("✅ Роли созданы")


def create_business_elements():
    """Создаем бизнес-элементы"""
    elements_data = [
        ('user', 'Пользователи системы'),
        ('product', 'Товары/книги'),
        ('category', 'Категории товаров'),
        ('order', 'Заказы'),
        ('cart', 'Корзина покупок'),
        ('review', 'Отзывы на товары'),
        ('permission', 'Права доступа'),
    ]

    for name, description in elements_data:
        BusinessElement.objects.get_or_create(
            name=name,
            defaults={'description': description}
        )
    print("✅ Бизнес-элементы созданы")


def create_access_rules():
    """Создаем базовые правила доступа"""

    # Получаем роли
    admin_role = Role.objects.get(name='admin')
    manager_role = Role.objects.get(name='manager')
    customer_role = Role.objects.get(name='customer')
    guest_role = Role.objects.get(name='guest')

    # Получаем все элементы
    elements = BusinessElement.objects.all()

    # Правила для Администратора (полный доступ ко всему)
    for element in elements:
        AccessRule.objects.get_or_create(
            role=admin_role,
            element=element,
            defaults={
                'read_permission': True,
                'read_all_permission': True,
                'create_permission': True,
                'update_permission': True,
                'update_all_permission': True,
                'delete_permission': True,
                'delete_all_permission': True,
            }
        )

    # Правила для Менеджера
    manager_elements = ['product', 'category', 'order', 'review']
    for element_name in manager_elements:
        element = BusinessElement.objects.get(name=element_name)
        AccessRule.objects.get_or_create(
            role=manager_role,
            element=element,
            defaults={
                'read_permission': True,
                'read_all_permission': True,
                'create_permission': True,
                'update_permission': True,
                'update_all_permission': True,
                'delete_permission': True,
                'delete_all_permission': True,
            }
        )

    # Правила для Покупателя
    customer_elements = ['product', 'category', 'order', 'cart', 'review']
    for element_name in customer_elements:
        element = BusinessElement.objects.get(name=element_name)
        if element_name in ['order', 'cart', 'review']:
            # Для своих заказов, корзины и отзывов
            AccessRule.objects.get_or_create(
                role=customer_role,
                element=element,
                defaults={
                    'read_permission': True,
                    'read_all_permission': False,
                    'create_permission': True,
                    'update_permission': True,
                    'update_all_permission': False,
                    'delete_permission': True,
                    'delete_all_permission': False,
                }
            )
        else:
            # Для товаров и категорий - только чтение
            AccessRule.objects.get_or_create(
                role=customer_role,
                element=element,
                defaults={
                    'read_permission': True,
                    'read_all_permission': True,
                    'create_permission': False,
                    'update_permission': False,
                    'update_all_permission': False,
                    'delete_permission': False,
                    'delete_all_permission': False,
                }
            )

    # Правила для Гостя
    guest_elements = ['product', 'category']
    for element_name in guest_elements:
        element = BusinessElement.objects.get(name=element_name)
        AccessRule.objects.get_or_create(
            role=guest_role,
            element=element,
            defaults={
                'read_permission': True,
                'read_all_permission': True,
                'create_permission': False,
                'update_permission': False,
                'update_all_permission': False,
                'delete_permission': False,
                'delete_all_permission': False,
            }
        )

    print("✅ Правила доступа созданы")


def create_superuser():
    """Создаем суперпользователя"""
    if not User.objects.filter(email='admin@gmail.com').exists():
        User.objects.create_superuser(
            email='admin@gmail.com',
            username='admin',
            password='admin123'
        )
        print("✅ Суперпользователь создан: admin@gmail.com / admin123")
    else:
        print("ℹ️ Суперпользователь уже существует")


def main():
    """Основная функция заполнения данных"""
    print("Начинаем заполнение начальных данных...")

    create_roles()
    create_business_elements()
    create_access_rules()
    create_superuser()

    print("\n🎉 Заполнение данных завершено!")
    print("\nДоступные пользователи для тестирования:")
    print("1. Администратор: admin@gmail.com / admin123")
    print("\nРоли и права настроены согласно ТЗ:")


if __name__ == '__main__':
    main()