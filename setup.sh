#!/bin/bash
# setup.sh

echo "Начинаем настройку проекта BookHub..."

# Создаем виртуальное окружение
echo "Создаем виртуальное окружение..."
python3 -m venv venv
source venv/bin/activate  # Было: source venb/bin/activate

# Устанавливаем зависимости
echo "Устанавливаем зависимости..."
pip install --upgrade pip
pip install -r requirements.txt

# Запускаем Docker контейнеры
echo "Запускаем PostgreSQL и Redis..."
docker-compose up -d

# Ждем готовности БД
echo "Ждем готовности базы данных..."
sleep 10

# Создаем миграции
echo "Создаем миграции..."
python manage.py makemigrations

# Применяем миграции
echo "Применяем миграции..."
python manage.py migrate

# Создаем тестовые данные
echo "Создаем тестовые данные..."
python scripts/seed_data.py
python manage.py create_test_users --force
python scripts/create_test_products.py

echo "Настройка завершена!"
echo "Запуск сервера: python manage.py runserver"
echo "Админка: http://localhost:8000/admin"
