#!/bin/bash
set -e

echo "Проверка подключения к PostgreSQL..."
while ! pg_isready -h postgres -p 5432 -U ${DB_USER}; do
    echo "Ожидание PostgreSQL..."
    sleep 2
done
echo "PostgreSQL готов!"

echo "Проверка подключения к Redis..."
while ! redis-cli -h redis ping | grep -q "PONG"; do
    echo "Ожидание Redis..."
    sleep 2
done
echo "Redis готов!"

echo "Применение миграций..."
python manage.py migrate --noinput

echo "Сбор статических файлов..."
python manage.py collectstatic --noinput

echo "Запуск сервера..."
exec python manage.py runserver 0.0.0.0:8000