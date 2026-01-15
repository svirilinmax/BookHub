import os
import sys

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bookhub.settings")
django.setup()

from apps.products.models import Category, Product  # noqa: E402
from apps.users.models import User  # noqa: E402


def clear_existing_data():
    """Очистка существующих тестовых данных"""
    print("Очистка старых тестовых данных...")

    # Удаляем только тестовые товары
    Product.objects.all().delete()
    print("Старые товары удалены")

    # Удаляем только тестовые категории
    Category.objects.filter(
        name__in=[
            "Художественная литература",
            "Научная литература",
            "Бизнес-литература",
            "Техническая литература",
            "Детская литература",
        ]
    ).delete()
    print("Старые категории удалены")


def create_test_categories():
    """Создаем тестовые категории"""
    print("\nСоздание категорий...")

    categories = [
        ("fiction", "Художественная литература", "Романы, рассказы, поэзия"),
        ("science", "Научная литература", "Учебники, научные труды"),
        ("business", "Бизнес-литература", "Маркетинг, менеджмент, финансы"),
        ("tech", "Техническая литература", "Программирование, инженерия"),
        ("children", "Детская литература", "Книги для детей"),
    ]

    created_categories = {}

    for slug, name, description in categories:
        # Проверяем существование
        existing = Category.objects.filter(slug=slug).first()
        if not existing:
            category = Category.objects.create(
                name=name, slug=slug, description=description
            )
            print(f"  Создана: {name}")
        else:
            category = existing
            print(f"  Уже существует: {name}")

        created_categories[slug] = category

    return created_categories


def create_test_products(categories):
    """
    Создаем тестовые товары
    """
    print("\nСоздание товаров...")

    # Получаем или создаем администратора
    admin, created = User.objects.get_or_create(
        email="admin@gmail.com",
        defaults={
            "username": "admin",
            "password": "admin123",
            "is_staff": True,
            "is_superuser": True,
        },
    )

    if created:
        admin.set_password("admin123")
        admin.save()
        print("Создан администратор")

    products = [
        {
            "title": "Мастер и Маргарита",
            "author": "Михаил Булгаков",
            "description": "Классический роман о добре и зле. "
            "Москва 1930-х годов становится ареной "
            "борьбы между силами добра и зла.",
            "price": 450.00,
            "category": categories["fiction"],
            "stock": 10,
            "owner": admin,
        },
        {
            "title": "Чистый код",
            "author": "Роберт Мартин",
            "description": "Создание, анализ и рефакторинг кода. "
            "Практическое руководство по написанию "
            "чистого и поддерживаемого кода.",
            "price": 1200.00,
            "category": categories["tech"],
            "stock": 5,
            "owner": admin,
        },
        {
            "title": "Python. К вершинам мастерства",
            "author": "Лучано Рамальо",
            "description": "Продвинутое руководство по Python. "
            "Подробное описание возможностей "
            "Python 3 для опытных разработчиков.",
            "price": 1500.00,
            "category": categories["tech"],
            "stock": 8,
            "owner": admin,
        },
        {
            "title": "7 навыков высокоэффективных людей",
            "author": "Стивен Кови",
            "description": "Мощные инструменты развития личности. "
            "Классика бизнес-литературы о личной эффективности.",
            "price": 800.00,
            "category": categories["business"],
            "stock": 15,
            "owner": admin,
        },
        {
            "title": "1984",
            "author": "Джордж Оруэлл",
            "description": "Антиутопический роман о тоталитаризме. "
            "Предупреждение о опасностях тоталитарного общества.",
            "price": 500.00,
            "category": categories["fiction"],
            "stock": 7,
            "owner": admin,
        },
        {
            "title": "Краткая история времени",
            "author": "Стивен Хокинг",
            "description": "От Большого взрыва до черных дыр. "
            "Популярное изложение космологии для "
            "широкого круга читателей.",
            "price": 750.00,
            "category": categories["science"],
            "stock": 12,
            "owner": admin,
        },
        {
            "title": "Гарри Поттер и философский камень",
            "author": "Джоан Роулинг",
            "description": "Первая книга о юном волшебнике. "
            "Начало приключений Гарри Поттера "
            "в школе магии Хогвартс.",
            "price": 600.00,
            "category": categories["children"],
            "stock": 20,
            "owner": admin,
        },
    ]

    created_count = 0
    for product_data in products:
        if not Product.objects.filter(title=product_data["title"]).exists():
            Product.objects.create(**product_data)
            created_count += 1
            print(f"  Создан: {product_data['title']}")
        else:
            print(f"  Уже существует: {product_data['title']}")

    return created_count


def main():
    """Основная функция"""
    print("Создание тестовых данных для BookHub")
    print("=" * 50)

    # Очищаем старые данные
    clear_existing_data()

    # Создаем категории
    categories = create_test_categories()

    # Создаем товары
    created_count = create_test_products(categories)

    print("\n" + "=" * 50)
    print("Тестовые данные созданы!")
    print(f"Итог: {created_count} новых товаров, {Category.objects.count()} категорий")

    # Выводим список товаров
    print("\nДоступные товары:")
    for product in Product.objects.all():
        print(f"  • {product.title} - {product.author} ({product.price} руб.)")

    print("\nАдминистратор: admin@gmail.com / admin123")


if __name__ == "__main__":
    main()
