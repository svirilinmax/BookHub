@echo off
REM setup.bat

echo Начинаем настройку проекта BookHub...

REM Создаем виртуальное окружение
echo Создаем виртуальное окружение...
python -m venv venv
call venv\Scripts\activate

REM Устанавливаем зависимости
echo Устанавливаем зависимости...
pip install --upgrade pip
pip install -r requirements.txt

REM Создаем .env файл если его нет
if not exist .env (
    echo Создаем файл .env...
    copy .env.example .env
    echo Пожалуйста, откройте файл .env и настройте параметры!
)

REM Запускаем Docker контейнеры
echo Запускаем PostgreSQL и Redis...
docker-compose up -d

REM Ждем готовности БД
echo Ждем готовности базы данных...
timeout /t 10 /nobreak

REM Создаем миграции
echo Создаем миграции...
python manage.py makemigrations

REM Применяем миграции
echo Применяем миграции...
python manage.py migrate

REM Создаем тестовые данные
echo Создаем тестовые данные...
python scripts/seed_data.py

REM Создаем суперпользователя
echo Создаем суперпользователя...
python manage.py create_test_users --force

echo Настройка завершена!
echo Запуск сервера: python manage.py runserver
echo Админка: http://localhost:8000/admin
echo Для Docker используйте: docker-compose up