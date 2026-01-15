import os
import sys

import django
import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bookhub.settings")
django.setup()

BASE_URL = "http://127.0.0.1:8000"


def quick_test():
    """
    Быстрый тест основных функций
    """
    print("Быстрый тест BookHub")
    print("=" * 40)

    # 1. Проверка сервера
    print("1. Проверка сервера...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=3)
        print(f"Сервер доступен ({response.status_code})")
    except Exception as e:
        print("Сервер не доступен!")
        print(f"Ошибка: {str(e)}")
        print("Запустите: python manage.py runserver")
        return

    # 2. Проверка публичного API
    print("\n2. Проверка публичного API...")
    response = requests.get(f"{BASE_URL}/api/products/")
    print(f"   GET /api/products/: {response.status_code}")

    # 3. Проверка аутентификации
    print("\n3. Проверка аутентификации...")

    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login/",
            json={"email": "admin@gmail.com", "password": "admin123"},
            headers={"Content-Type": "application/json"},
        )

        if response.status_code == 200:
            print("Админ может залогиниться")
            token = response.json()["tokens"]["access"]

            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{BASE_URL}/api/auth/profile/", headers=headers)
            print(f"GET профиль: {response.status_code}")
        else:
            print(f"Ошибка логина админа: {response.status_code}")

    except Exception as e:
        print(f"Ошибка: {str(e)}")

    print("\n" + "=" * 40)
    print("Команды для дальнейшего тестирования:")
    print("• Полный тест: python scripts/master_test_script.py")
    print("• Создать данные: python manage.py create_test_users --force")
    print("• Запустить товары: python scripts/create_test_products.py")


if __name__ == "__main__":
    quick_test()
