# scripts/master_test_script.py - ИСПРАВЛЕННАЯ ВЕРСИЯ
"""
📚 BOOKHUB - МАСТЕР СКРИПТ ДЛЯ ТЕСТИРОВАНИЯ
Объединяет все функции: создание данных и тестирование всех сценариев
"""

import os
import sys
import django
import requests
import json
import time
from datetime import datetime

# Настройка Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookhub.settings')
django.setup()

BASE_URL = 'http://127.0.0.1:8000'

# Импорты Django моделей
from django.contrib.auth import get_user_model
from apps.authorization.models import Role, BusinessElement, AccessRule, UserRole
from apps.products.models import Product, Category
from apps.orders.models import CartItem, Order

User = get_user_model()


class BookHubMasterTester:
    def __init__(self):
        self.results = []
        self.tokens = {}
        self.product_id = None
        self.category_id = None
        self.headers = {'Content-Type': 'application/json; charset=utf-8'}

    def log_step(self, message, success=True):
        """Логирует шаг выполнения"""
        emoji = "✅" if success else "❌"
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {emoji} {message}")
        return success

    def check_server(self):
        """Проверяет, запущен ли сервер"""
        print("🔍 Проверка подключения к серверу...")
        try:
            response = requests.get(f"{BASE_URL}/", timeout=5)
            if response.status_code == 200:
                return self.log_step("Сервер запущен и доступен")
            else:
                return self.log_step(f"Сервер ответил с кодом: {response.status_code}", False)
        except Exception as e:
            return self.log_step(f"Сервер не доступен: {str(e)}", False)

    def create_test_data(self):
        """Создает тестовые данные: пользователи, роли, товары"""
        print("\n📊 СОЗДАНИЕ ТЕСТОВЫХ ДАННЫХ")
        print("=" * 50)

        # 1. Создаем суперпользователя
        try:
            admin, created = User.objects.get_or_create(
                email='admin@gmail.com',
                defaults={
                    'username': 'admin',
                    'is_staff': True,
                    'is_superuser': True,
                    'is_verified': True
                }
            )
            if created or not admin.check_password('admin123'):
                admin.set_password('admin123')
                admin.save()
                self.log_step(f"Администратор: admin@gmail.com / admin123")
        except Exception as e:
            self.log_step(f"Ошибка создания администратора: {str(e)}", False)

        # 2. Создаем тестовых пользователей
        test_users = [
            ('customer@test.com', 'customer', 'Test123!'),
            ('manager@test.com', 'manager', 'Test123!'),
            ('customer1@test.com', 'customer', 'Test123!'),
        ]

        for email, role_name, password in test_users:
            try:
                user, created = User.objects.get_or_create(
                    email=email,
                    defaults={
                        'username': email.split('@')[0],
                        'is_verified': True,
                        'is_active': True
                    }
                )

                if created or not user.check_password(password):
                    user.set_password(password)
                    user.save()

                # Назначаем роль
                try:
                    role = Role.objects.get(name=role_name)
                    UserRole.objects.get_or_create(user=user, role=role)
                    self.log_step(f"{role_name}: {email} / {password}")
                except Role.DoesNotExist:
                    self.log_step(f"Роль '{role_name}' не найдена для {email}", False)

            except Exception as e:
                self.log_step(f"Ошибка создания пользователя {email}: {str(e)}", False)

        # 3. Создаем тестовые категории и товары
        try:
            # Категории
            categories_data = [
                ('fiction', 'Художественная литература', 'Романы, рассказы, поэзия'),
                ('tech', 'Техническая литература', 'Программирование, инженерия'),
                ('business', 'Бизнес-литература', 'Маркетинг, менеджмент, финансы'),
            ]

            categories = {}
            for slug, name, description in categories_data:
                cat, _ = Category.objects.get_or_create(
                    slug=slug,
                    defaults={'name': name, 'description': description}
                )
                categories[slug] = cat
                self.category_id = str(cat.id)  # Сохраняем ID категории для тестов

            # Товары
            products_data = [
                {
                    'title': 'Мастер и Маргарита',
                    'author': 'Михаил Булгаков',
                    'description': 'Классический роман о добре и зле',
                    'price': 450.00,
                    'category': categories['fiction'],
                    'stock': 10,
                },
                {
                    'title': 'Чистый код',
                    'author': 'Роберт Мартин',
                    'description': 'Создание, анализ и рефакторинг кода',
                    'price': 1200.00,
                    'category': categories['tech'],
                    'stock': 5,
                },
            ]

            for product_data in products_data:
                Product.objects.get_or_create(
                    title=product_data['title'],
                    defaults=product_data
                )

            self.log_step(f"Создано {Product.objects.count()} товаров и {Category.objects.count()} категорий")

        except Exception as e:
            self.log_step(f"Ошибка создания товаров: {str(e)}", False)

        return True

    def get_auth_tokens(self):
        """Получает JWT токены для всех тестовых пользователей"""
        print("\n🔐 ПОЛУЧЕНИЕ ТОКЕНОВ АУТЕНТИФИКАЦИИ")
        print("=" * 50)

        users = [
            ('customer@test.com', 'Test123!', 'customer'),
            ('manager@test.com', 'Test123!', 'manager'),
            ('admin@gmail.com', 'admin123', 'admin'),
        ]

        for email, password, role in users:
            try:
                response = requests.post(
                    f"{BASE_URL}/api/auth/login/",
                    json={'email': email, 'password': password},
                    headers=self.headers
                )

                if response.status_code == 200:
                    token = response.json()['tokens']['access']
                    self.tokens[role] = token
                    self.log_step(f"Токен для {role} получен")
                else:
                    self.log_step(f"Не удалось получить токен для {email}: {response.status_code}", False)

            except Exception as e:
                self.log_step(f"Ошибка получения токена для {email}: {str(e)}", False)

        return len(self.tokens) > 0

    def find_test_product(self):
        """Находит товар для тестов"""
        print("\n📦 ПОИСК ТОВАРА ДЛЯ ТЕСТОВ")
        print("=" * 50)

        try:
            # Получаем список товаров
            response = requests.get(f"{BASE_URL}/api/products/", headers=self.headers)
            if response.status_code == 200:
                data = response.json()

                if isinstance(data, dict) and 'results' in data and data['results']:
                    # Пагинированный ответ
                    self.product_id = data['results'][0]['id']

                    # Получаем категорию товара
                    product_data = data['results'][0]
                    if 'category' in product_data and product_data['category']:
                        self.category_id = product_data['category']['id'] if isinstance(product_data['category'],
                                                                                        dict) else product_data[
                            'category']

                    self.log_step(f"Найден товар для тестов: {self.product_id}")

                    # Если нет категории, получаем первую категорию
                    if not self.category_id:
                        cat_response = requests.get(f"{BASE_URL}/api/products/categories/", headers=self.headers)
                        if cat_response.status_code == 200:
                            cats = cat_response.json()
                            if isinstance(cats, dict) and 'results' in cats and cats['results']:
                                self.category_id = cats['results'][0]['id']
                                self.log_step(f"Найдена категория: {self.category_id}")

                    return True

        except Exception as e:
            self.log_step(f"Ошибка поиска товара: {str(e)}", False)

        return False

    def run_basic_scenarios(self):
        """Запускает базовые сценарии из ТЗ"""
        print("\n📋 ТЕСТИРОВАНИЕ ОСНОВНЫХ СЦЕНАРИЕВ ИЗ ТЗ")
        print("=" * 50)

        # Сначала находим товар и категорию
        if not self.find_test_product():
            self.log_step("Не удалось найти товар для тестов", False)
            return False

        scenarios = [
            # Сценарий 1: Гость просматривает товары
            {
                'name': 'Гость: GET /api/products/ → 200',
                'method': 'GET',
                'url': '/api/products/',
                'expected': 200,
                'token': None
            },
            # Сценарий 2: Гость пытается создать заказ
            {
                'name': 'Гость: POST /api/orders/orders/ → 401',
                'method': 'POST',
                'url': '/api/orders/orders/',
                'expected': 401,
                'token': None,
                'data': {'total_amount': 100, 'shipping_address': 'Test'}
            },
            # Сценарий 3: Покупатель добавляет в корзину
            {
                'name': 'Покупатель: POST в корзину → 201',
                'method': 'POST',
                'url': '/api/orders/cart/items/',
                'expected': 201,
                'token': self.tokens.get('customer'),
                'data': {'product_id': self.product_id, 'quantity': 1}  # Используем product_id
            },
            # Сценарий 4: Покупатель пытается удалить товар
            {
                'name': 'Покупатель: DELETE товар → 403',
                'method': 'DELETE',
                'url': f'/api/products/{self.product_id}/',
                'expected': 403,
                'token': self.tokens.get('customer')
            },
            # Сценарий 5: Менеджер обновляет товар
            {
                'name': 'Менеджер: PUT товар → 200',
                'method': 'PUT',
                'url': f'/api/products/{self.product_id}/',
                'expected': 200,
                'token': self.tokens.get('manager'),
                'data': {
                    'title': 'Обновлено менеджером',
                    'author': 'Автор менеджера',  # Обязательное поле
                    'description': 'Обновленное описание менеджера',  # Обязательное поле
                    'price': 999.99,
                    'category': self.category_id  # Обязательное поле
                }
            },
            # Сценарий 6: Админ имеет полный доступ
            {
                'name': 'Админ: GET товары → 200',
                'method': 'GET',
                'url': '/api/products/',
                'expected': 200,
                'token': self.tokens.get('admin')
            }
        ]

        # Запускаем сценарии
        passed = 0
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n🧪 Сценарий {i}: {scenario['name']}")

            # Проверяем, есть ли токен для этого сценария
            if scenario.get('token') is None or scenario['token']:
                success, response = self._test_scenario(scenario)
                if success:
                    passed += 1
                else:
                    # Выводим детали ошибки
                    if response and response.text:
                        try:
                            error_data = response.json()
                            print(f"  📝 Ответ: {json.dumps(error_data, ensure_ascii=False)[:200]}")
                        except:
                            print(f"  📝 Ответ: {response.text[:200]}")
            else:
                print(f"⚠️ Пропущен (нет токена для роли)")

        print(f"\n📊 Результат: {passed}/{len(scenarios)} сценариев пройдено")
        return passed == len(scenarios)

    def _test_scenario(self, scenario):
        """Тестирует один сценарий, возвращает (success, response)"""
        url = f"{BASE_URL}{scenario['url']}"
        headers = self.headers.copy()

        if scenario.get('token'):
            headers['Authorization'] = f'Bearer {scenario["token"]}'

        try:
            if scenario['method'] == 'GET':
                response = requests.get(url, headers=headers)
            elif scenario['method'] == 'POST':
                response = requests.post(url, headers=headers, json=scenario.get('data', {}))
            elif scenario['method'] == 'PUT':
                response = requests.put(url, headers=headers, json=scenario.get('data', {}))
            elif scenario['method'] == 'DELETE':
                response = requests.delete(url, headers=headers)
            elif scenario['method'] == 'PATCH':
                response = requests.patch(url, headers=headers, json=scenario.get('data', {}))
            else:
                return False, None

            success = response.status_code == scenario['expected']
            status = "✅" if success else "❌"
            print(f"  {status} Ожидалось: {scenario['expected']}, Получено: {response.status_code}")

            return success, response

        except Exception as e:
            print(f"  ❌ Ошибка: {str(e)}")
            return False, None

    def test_rbac_system(self):
        """Тестирует работу RBAC системы"""
        print("\n🔐 ТЕСТИРОВАНИЕ RBAC СИСТЕМЫ")
        print("=" * 50)

        tests = []

        # Тест 1: Проверка ролей в системе
        try:
            role_count = Role.objects.count()
            tests.append(self.log_step(f"Ролей в системе: {role_count}", role_count >= 4))
        except Exception as e:
            tests.append(self.log_step(f"Ошибка проверки ролей: {str(e)}", False))

        # Тест 2: Проверка бизнес-элементов
        try:
            element_count = BusinessElement.objects.count()
            tests.append(self.log_step(f"Бизнес-элементов: {element_count}", element_count >= 7))
        except Exception as e:
            tests.append(self.log_step(f"Ошибка проверки элементов: {str(e)}", False))

        # Тест 3: Проверка правил доступа
        try:
            rule_count = AccessRule.objects.count()
            tests.append(self.log_step(f"Правил доступа: {rule_count}", rule_count >= 18))
        except Exception as e:
            tests.append(self.log_step(f"Ошибка проверки правил: {str(e)}", False))

        # Тест 4: Проверка админского API
        if self.tokens.get('admin'):
            try:
                headers = {'Authorization': f'Bearer {self.tokens["admin"]}'}
                response = requests.get(f"{BASE_URL}/api/admin/permissions/roles/", headers=headers)
                tests.append(self.log_step("Админский API доступен", response.status_code == 200))
            except Exception as e:
                tests.append(self.log_step(f"Ошибка проверки админского API: {str(e)}", False))

        passed = sum(1 for test in tests if test)
        print(f"\n📊 Результат RBAC тестов: {passed}/{len(tests)} пройдено")
        return passed == len(tests)

    def run_comprehensive_test(self):
        """Запускает комплексное тестирование"""
        print("\n" + "=" * 60)
        print("🚀 ЗАПУСК КОМПЛЕКСНОГО ТЕСТИРОВАНИЯ BOOKHUB")
        print("=" * 60)

        # Шаг 1: Проверка сервера
        if not self.check_server():
            print("\n❌ Сервер не доступен! Запустите:")
            print("   python manage.py runserver")
            return False

        # Шаг 2: Создание тестовых данных (опционально)
        print("\n📝 Для создания тестовых данных запустите отдельно:")
        print("   python scripts/master_test_script.py --create-only")

        # Шаг 3: Получение токенов
        if not self.get_auth_tokens():
            print("\n⚠️ Не удалось получить токены. Проверьте:")
            print("   1. Запущен ли сервер")
            print("   2. Существуют ли тестовые пользователи")
            print("   3. Правильные ли пароли")
            return False

        # Шаг 4: Тестирование RBAC
        self.test_rbac_system()

        # Шаг 5: Запуск основных сценариев
        success = self.run_basic_scenarios()

        print("\n" + "=" * 60)
        print("🎉 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")
        print("=" * 60)

        if success:
            print("\n✅ ВСЕ СЦЕНАРИИ ИЗ ТЗ ПРОЙДЕНЫ!")
            print("🎊 Система BookHub готова к сдаче!")
        else:
            print("\n⚠️ НЕ ВСЕ СЦЕНАРИИ ПРОЙДЕНЫ")
            print("Проверьте логи выше для деталей")

        print("\n👤 ТЕСТОВЫЕ ПОЛЬЗОВАТЕЛИ:")
        print("  • Админ: admin@gmail.com / admin123")
        print("  • Менеджер: manager@test.com / Test123!")
        print("  • Покупатель: customer@test.com / Test123!")

        return success


def main():
    """Основная функция"""
    import argparse

    parser = argparse.ArgumentParser(description='Мастер скрипт для тестирования BookHub')
    parser.add_argument('--create-only', action='store_true', help='Только создать тестовые данные')
    parser.add_argument('--test-only', action='store_true', help='Только запустить тесты')

    args = parser.parse_args()

    tester = BookHubMasterTester()

    if args.create_only:
        # Только создание данных
        tester.create_test_data()
    elif args.test_only:
        # Только тестирование
        tester.check_server()
        tester.get_auth_tokens()
        tester.run_basic_scenarios()
    else:
        # Полный цикл
        tester.run_comprehensive_test()


if __name__ == '__main__':
    main()