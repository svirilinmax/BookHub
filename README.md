# BookHub - Интернет-магазин книг с кастомной RBAC системой

![Django](https://img.shields.io/badge/Django-5.2.5-092E20?logo=django)
![DRF](https://img.shields.io/badge/DRF-3.15.0-9C1A1C?logo=django)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791?logo=postgresql)
![JWT](https://img.shields.io/badge/JWT-Authentication-000000?logo=jsonwebtokens)
![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)

## О проекте

**BookHub** — backend-приложение интернет-магазина книг с полностью кастомной системой аутентификации и авторизации. Проект разработан с акцентом на собственную реализацию механизмов контроля доступа вместо использования стандартных решений Django "из коробки".

### Ключевые особенности
- **Кастомная система аутентификации** на JWT токенах
- **Полноценная RBAC система** с ролями: guest, customer, manager, admin
- **Docker окружение** с PostgreSQL и Redis "из коробки"
- **Готовый к продакшену** код с полной документацией
- **Модульная архитектура** с разделением ответственности

## Быстрый старт

### Предварительные требования
- **Docker** и **Docker Compose**
- Git для клонирования репозитория

### Вариант 1: Автоматическая установка (рекомендуется)

Проект включает скрипты автоматической настройки для разных операционных систем:

#### Для Windows:
```batch
# Запустите setup.bat в корне проекта
setup.bat
```

#### Для Linux/Mac:
```bash
# Дайте права на выполнение и запустите
chmod +x setup.sh
./setup.sh
```

**Что делают скрипты:**
1. Создает виртуальное окружение Python
2. Устанавливает все зависимости
3. Запускает Docker контейнеры (PostgreSQL + Redis)
4. Применяет миграции базы данных
5. Создает тестовые данные и пользователей
6. Добавляет тестовые товары в каталог

### Вариант 2: Ручная установка через Docker

```bash

# 1. Клонирование репозитория
git clone https://github.com/svirilinmax/BookHub.git
cd BookHub/bookhub

# 2. Запуск инфраструктуры
docker-compose up -d

# 3. Инициализация тестовых данных
docker-compose exec web python scripts/setup.py

# Проверка работы
curl http://localhost:8000/api/products/
```

Система доступна по адресу `http://localhost:8000`

### Вариант 3: Альтернативный запуск (без Docker)
```bash

# Создание виртуального окружения
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# или
.venv\Scripts\activate      # Windows

# Установка зависимостей
pip install -r requirements.txt

# Настройка базы данных
python manage.py migrate

# Создание тестовых данных
python scripts/setup.py

# Запуск сервера
python manage.py runserver
```

### Сравнение методов установки

| Метод | Сложность | Время | Лучше для |
|-------|-----------|-------|-----------|
| **setup.bat / setup.sh** | Легко | 5-10 мин | Начальной настройки |
| **Ручная Docker установка** | Средне | 10-15 мин | Понимания процесса |
| **Без Docker** | Средне | 15-20 мин | Разработки без Docker |

## Архитектура проекта

### Структура каталогов
```
bookhub/
├── apps/                           # Модули приложения
│   ├── authentication/            # Кастомная аутентификация
│   ├── authorization/             # RBAC система
│   ├── users/                     # Модель пользователя
│   ├── products/                  # Товары и категории
│   ├── orders/                    # Заказы и корзина
│   └── core/                      # Базовые модели
├── scripts/                       # Скрипты для работы
├── bookhub/                       # Конфигурация проекта
└── static/                        # Статические файлы
```

### Ключевые файлы для запуска
```
bookhub/
├── setup.bat                    # Автоматическая установка для Windows
├── setup.sh                     # Автоматическая установка для Linux/Mac
├── docker-compose.yml          # Docker контейнеры (PostgreSQL + Redis)
├── requirements.txt            # Python зависимости
├── scripts/
│   ├── setup.py               # Основной скрипт инициализации
│   ├── seed_data.py           # Начальные данные RBAC
│   ├── create_test_products.py # Тестовые товары
│   └── master_test_script.py  # Тестирование всех сценариев
└── .env.example               # Шаблон переменных окружения
```

### Технологический стек
| Компонент | Технология | Назначение |
|-----------|------------|------------|
| **Backend** | Django 5.2 + DRF 3.15 | Основной фреймворк |
| **База данных** | PostgreSQL 15 | Основное хранилище |
| **Кэширование** | Redis 7 | Сессии и токены |
| **Аутентификация** | JWT + кастомная реализация | Управление доступом |
| **Контейнеризация** | Docker + Docker Compose | Развертывание |
| **Документация** | drf-yasg/Swagger | API документация |

## Модель данных

### Основные сущности
```sql
-- Пользователи
users (id, email, password_hash, first_name, last_name, is_active)

-- RBAC система
roles (id, name, description)                          -- Роли пользователей
business_elements (id, name, description)              -- Бизнес-элементы
access_roles_rules (id, role_id, element_id, ...)      -- Правила доступа

-- Бизнес-логика
products (id, title, author, price, category_id)       -- Товары
categories (id, name, parent_id)                       -- Категории
orders (id, customer_id, status, total_amount)         -- Заказы
cart_items (id, user_id, product_id, quantity)         -- Корзина
reviews (id, product_id, user_id, rating, text)        -- Отзывы
```

## Система ролей и прав (RBAC)

### Роли пользователей
| Роль | Описание | Типичные права |
|------|----------|----------------|
| **Гость** | Неавторизованный пользователь | Чтение товаров и категорий |
| **Покупатель** | Зарегистрированный клиент | Управление корзиной, создание заказов и отзывов |
| **Менеджер** | Сотрудник магазина | Управление товарами, категориями, заказами |
| **Администратор** | Администратор системы | Полный доступ, управление правами |

### Бизнес-элементы
Система контролирует доступ к 7 бизнес-элементам:
1. `user` — пользователи системы
2. `product` — товары/книги
3. `category` — категории товаров
4. `order` — заказы
5. `cart` — корзина покупок
6. `review` — отзывы на товары
7. `permission` — права доступа

### Матрица прав доступа (пример)
| Роль → <br> Элемент ↓ | Чтение | Создание | Обновление | Удаление |
|----------------------|--------|----------|------------|----------|
| **Гость** <br> (product) | Все | - | - | - |
| **Покупатель** <br> (order) | Свои | Да | Свои | Свои |
| **Менеджер** <br> (product) | Все | Да | Все | Все |
| **Админ** <br> (user) | Все | Да | Все | Все |

## API Endpoints

### Аутентификация
| Метод | Endpoint | Описание | Доступ |
|-------|----------|----------|---------|
| `POST` | `/api/auth/login/` | Вход в систему | Публичный |
| `POST` | `/api/auth/register/` | Регистрация | Публичный |
| `GET` | `/api/auth/profile/` | Профиль пользователя | Аутентиф. |
| `POST` | `/api/auth/logout/` | Выход из системы | Аутентиф. |
| `POST` | `/api/auth/refresh/` | Обновление токена | Аутентиф. |

### Товары
| Метод | Endpoint | Описание | Доступ |
|-------|----------|----------|---------|
| `GET` | `/api/products/` | Список товаров | Публичный |
| `POST` | `/api/products/` | Создание товара | Менеджер+ |
| `GET` | `/api/products/{id}/` | Детали товара | Публичный |
| `PUT` | `/api/products/{id}/` | Обновление товара | Менеджер+ |
| `DELETE` | `/api/products/{id}/` | Удаление товара | Админ |

### Заказы и корзина
| Метод | Endpoint | Описание | Доступ |
|-------|----------|----------|---------|
| `GET` | `/api/orders/cart/items/` | Элементы корзины | Покупатель |
| `POST` | `/api/orders/cart/items/` | Добавить в корзину | Покупатель |
| `POST` | `/api/orders/orders/` | Создать заказ | Покупатель |
| `GET` | `/api/orders/orders/` | Мои заказы | Покупатель |

### Права Админа
| Метод | Endpoint | Описание | Доступ |
|-------|----------|----------|---------|
| `GET` | `/api/admin/permissions/roles/` | Список ролей | Админ |
| `GET` | `/api/admin/permissions/elements/` | Бизнес-элементы | Админ |
| `GET` | `/api/admin/permissions/rules/` | Правила доступа | Админ |

## Тестирование

### Тестовые пользователи
```
Администратор:
  • Email: admin@gmail.com
  • Пароль: admin123
  • Доступ: Полный (все операции)

Менеджер:
  • Email: manager@test.com
  • Пароль: Test123!
  • Доступ: Управление товарами и заказами

Покупатель:
  • Email: customer@test.com
  • Пароль: Test123!
  • Доступ: Заказы, корзина, отзывы
```

### Сценарии из ТЗ (все протестированы)
```
Сценарий 1: Гость может просматривать товары
  GET /api/products/ → 200 OK

Сценарий 2: Гость не может создавать заказы
  POST /api/orders/orders/ → 401 Unauthorized

Сценарий 3: Покупатель может добавлять в корзину
  POST /api/orders/cart/items/ → 201 Created

Сценарий 4: Покупатель не может удалять товары
  DELETE /api/products/1/ → 403 Forbidden

Сценарий 5: Менеджер может обновлять товары
  PUT /api/products/1/ → 200 OK

Сценарий 6: Админ имеет полный доступ
  GET /api/products/ → 200 OK
```

### Команды тестирования
```bash

# Полный тест всех сценариев
docker-compose exec web python scripts/master_test_script.py

# Быстрая проверка работы
docker-compose exec web python scripts/quick_test.py

# Только создание тестовых данных
docker-compose exec web python scripts/setup.py
```

### Скрипты для работы с данными
```bash

# Полная настройка системы
python scripts/setup.py

# Только RBAC данные (роли, элементы, права)
python scripts/seed_data.py

# Только тестовые товары
python scripts/create_test_products.py

# Пересоздание окружения
docker-compose down -v
docker-compose up -d --build
python scripts/setup.py
```

## Администрирование

### Docker команды
```bash

# Мониторинг состояния
docker-compose ps              # Статус контейнеров
docker-compose logs -f web     # Логи приложения

# Управление контейнерами
docker-compose stop           # Остановить все
docker-compose start          # Запустить все
docker-compose restart web    # Перезапустить приложение

# Доступ к сервисам
docker-compose exec postgres psql -U bookhub_user -d bookhub_db
docker-compose exec redis redis-cli
```

### Django команды
```bash

# Через Docker
docker-compose exec web python manage.py <command>

# Без Docker
python manage.py <command>

# Полезные команды:
python manage.py createsuperuser      # Создать администратора
python manage.py shell                # Открыть Django shell
python manage.py showmigrations       # Показать миграции
python manage.py check --deploy       # Проверка для продакшена
```

## Документация

### Доступ к документации API
После запуска приложения доступно:

| Ресурс | URL | Описание |
|--------|-----|----------|
| **Swagger UI** | http://localhost:8000/swagger/ | Интерактивная документация |
| **ReDoc** | http://localhost:8000/redoc/ | Альтернативная документация |
| **Админ-панель** | http://localhost:8000/admin/ | Администрирование |
| **OpenAPI JSON** | http://localhost:8000/swagger.json | Спецификация API |

### Пример запроса через cURL
```bash

# Получение токена
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "customer@test.com", "password": "Test123!"}'

# Использование токена
curl -X GET http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Docker окружение

### Сервисы
```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: bookhub_db
      POSTGRES_USER: bookhub_user
      POSTGRES_PASSWORD: bookhub_pass
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    environment:
      - DATABASE_URL=postgresql://bookhub_user:bookhub_pass@postgres:5432/bookhub_db
      - REDIS_URL=redis://redis:6379/0
```

### Переменные окружения
```env
# .env файл
DEBUG=False
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://bookhub_user:bookhub_pass@postgres:5432/bookhub_db
REDIS_URL=redis://redis:6379/0
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

## Поиск и устранение неисправностей

### Частые проблемы и решения

| Проблема | Решение |
|----------|---------|
| **Ошибка 401 Unauthorized** | Проверьте JWT токен в заголовке Authorization |
| **Ошибка 403 Forbidden** | Убедитесь, что пользователь имеет нужные права RBAC |
| **PostgreSQL не запускается** | Проверьте, не занят ли порт 5432: `netstat -an \| grep 5432` |
| **Redis connection error** | Убедитесь, что Redis запущен: `docker-compose ps redis` |
| **Миграции не применяются** | Выполните: `docker-compose exec web python manage.py migrate` |
| **Нет тестовых данных** | Запустите: `docker-compose exec web python scripts/setup.py` |

### Проблемы со скриптами установки

#### Проблема: Скрипт setup.sh не работает
```bash

# Дайте права на выполнение
chmod +x setup.sh

# Проверьте путь к Python
which python3

# Запустите с подробным выводом
bash -x setup.sh
```

#### Проблема: Скрипт setup.bat завершается с ошибкой
1. Проверьте, что Python добавлен в PATH
2. Убедитесь, что порты 5432 (PostgreSQL) и 6379 (Redis) свободны
3. Запустите командную строку от имени администратора

#### Проблема: Docker не запускается
```bash

# Проверьте статус Docker
docker --version
docker-compose --version

# Запустите Docker вручную
docker-compose up -d postgres redis
```

### Полезные команды отладки
```bash

# Проверка подключения к БД
docker-compose exec web python manage.py dbshell

# Проверка RBAC прав
docker-compose exec web python manage.py shell
>>> from apps.authorization.models import UserRole, AccessRule
>>> # Проверить роли пользователя

# Просмотр логов
docker-compose logs --tail=50 web
docker-compose logs --tail=50 postgres

# Очистка кэша Redis
docker-compose exec redis redis-cli FLUSHALL
```

### Ручное восстановление
Если скрипты не работают, выполните шаги вручную:
1. `python -m venv venv` и активация
2. `pip install -r requirements.txt`
3. `docker-compose up -d`
4. `python manage.py migrate`
5. `python scripts/setup.py`

## Развитие проекта

### Планируемые улучшения
1. **Email подтверждение** при регистрации
2. **Восстановление пароля** через email
3. **Поиск и фильтрация** товаров с Elasticsearch
4. **Панель аналитики** для менеджеров
5. **WebSocket уведомления** о статусе заказов
6. **Интеграция с платежными системами**

### Добавление новой функциональности
```python
# Пример: Добавление нового бизнес-элемента

# 1. Создать модель
class NewFeature(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    # ... другие поля

# 2. Добавить в бизнес-элементы
BusinessElement.objects.create(
    name='new_feature',
    description='Новая функциональность'
)

# 3. Настроить права доступа
AccessRule.objects.create(
    role=manager_role,
    element=new_feature_element,
    read_permission=True,
    create_permission=True,
    # ... другие права
)
```

## Вклад в проект

### Правила разработки
1. Следуйте **PEP 8** для Python кода
2. Используйте **типизацию** (type hints)
3. Пишите **тесты** для новой функциональности
4. Обновляйте **документацию**
5. Создавайте **Pull Requests** для изменений

### Установка для разработки
```bash

# Установка dev-зависимостей
pip install -r requirements-dev.txt

# Запуск тестов
pytest tests/

# Проверка качества кода
flake8 .
black --check .
mypy apps/
```

## Лицензия

Этот проект распространяется под лицензией **MIT**. Подробности см. в файле [LICENSE](LICENSE).

## Автор

**Разработано в рамках тестового задания**
Январь 2026
Контактная информация Telegram: https://t.me/svirilinmax

## Благодарности

- Команде **Django** за отличный фреймворк
- **Effective Mobile** за интересное техническое задание
- Сообществу **Open Source** за вдохновение

---

## Итоги выполнения ТЗ

| Требование ТЗ | Статус | Комментарий |
|--------------|--------|-------------|
| Кастомная аутентификация | Выполнено | JWT + собственная реализация |
| RBAC система | Выполнено | 4 роли, 7 бизнес-элементов |
| Регистрация/Логин/Выход | Выполнено | Полный цикл аутентификации |
| 401/403 ошибки | Выполнено | Корректная обработка |
| API для управления правами | Выполнено | Админские эндпоинты |
| Mock-объекты | Выполнено | Товары, заказы, корзина |
| Docker окружение | Выполнено | PostgreSQL + Redis |
| Тестирование | Выполнено | 6 сценариев из ТЗ |

---

**Совет**: Для демонстрации работы системы используйте команду `docker-compose exec web python scripts/master_test_script.py`, которая автоматически проверит все сценарии из технического задания.
```
