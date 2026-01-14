"""
📦 ЕДИНЫЙ СКРИПТ НАСТРОЙКИ BOOKHUB - ИСПРАВЛЕННАЯ ВЕРСИЯ
"""

import os
import sys
import django
from pathlib import Path

# Добавляем путь к проекту
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookhub.settings')
django.setup()


def setup_all():
    """Настраивает всю систему"""
    print("📦 Настройка BookHub...")

    # 1. Seed данные (роли, элементы)
    print("\n1. Создание RBAC структуры...")
    from scripts.seed_data import main as seed_main
    seed_main()

    # 2. Тестовые товары
    print("\n2. Создание тестовых товаров...")
    from scripts.create_test_products import main as products_main
    products_main()

    # 3. Тестовые пользователи
    print("\n3. Создание тестовых пользователей...")
    from django.contrib.auth import get_user_model
    from apps.authorization.models import Role, UserRole

    User = get_user_model()

    users = [
        ('admin@gmail.com', 'admin', 'admin123', True, True, None),  # Суперпользователь
        ('manager@test.com', 'manager', 'Test123!', False, False, 'manager'),  # Менеджер
        ('customer@test.com', 'customer', 'Test123!', False, False, 'customer'),  # Покупатель
    ]

    for email, username, password, is_staff, is_super, role_name in users:
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': username,
                'is_staff': is_staff,
                'is_superuser': is_super,
                'is_active': True,
                'is_verified': True
            }
        )

        # Устанавливаем пароль
        if created or not user.check_password(password):
            user.set_password(password)
            user.save()
            status = "создан" if created else "обновлен"
            print(f"   ✅ {email}: {password} ({status})")
        else:
            print(f"   ℹ️ {email}: уже существует")

        # Для менеджера: удаляем роль customer если она есть
        if email == 'manager@test.com':
            customer_role = Role.objects.filter(name='customer').first()
            if customer_role:
                UserRole.objects.filter(user=user, role=customer_role).delete()
                print(f"   🧹 Удалена лишняя роль 'customer' у менеджера")

        # Назначаем правильную роль
        if role_name and not is_super:
            try:
                role = Role.objects.get(name=role_name)
                UserRole.objects.get_or_create(user=user, role=role)
                print(f"   ✅ Назначена роль '{role_name}' для {email}")
            except Role.DoesNotExist:
                print(f"   ❌ Роль '{role_name}' не найдена для {email}")

    print("\n🎉 Настройка завершена!")

    # Проверяем роли
    print("\n🔍 Проверка назначенных ролей:")
    for email in ['manager@test.com', 'customer@test.com']:
        user = User.objects.get(email=email)
        roles = UserRole.objects.filter(user=user)
        role_names = [ur.role.name for ur in roles]
        print(f"   • {email}: {role_names}")

    print("\n👥 Тестовые пользователи:")
    print("   • Админ: admin@gmail.com / admin123")
    print("   • Менеджер: manager@test.com / Test123!")
    print("   • Покупатель: customer@test.com / Test123!")

    print("\n🚀 Запустите тесты:")
    print("   python scripts/master_test_script.py")


if __name__ == '__main__':
    setup_all()