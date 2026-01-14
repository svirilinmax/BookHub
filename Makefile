.PHONY: help build up down logs shell test clean reset migrate createsuperuser

help:
	@echo "Доступные команды:"
	@echo "  make build    - Собрать Docker образы"
	@echo "  make up       - Запустить контейнеры"
	@echo "  make down     - Остановить контейнеры"
	@echo "  make logs     - Показать логи"
	@echo "  make shell    - Зайти в контейнер Django"
	@echo "  make test     - Запустить тесты"
	@echo "  make clean    - Очистить всё"
	@echo "  make reset    - Полный перезапуск"
	@echo "  make migrate  - Применить миграции"
	@echo "  make createsuperuser - Создать суперпользователя"

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f web

shell:
	docker-compose exec web bash

test:
	docker-compose exec web python scripts/master_test_script.py --test-only

clean:
	docker-compose down -v
	docker system prune -f

reset: down clean build up
	@echo "✅ Система перезапущена"

migrate:
	docker-compose exec web python manage.py migrate

createsuperuser:
	docker-compose exec web python manage.py createsuperuser

db-shell:
	docker-compose exec postgres psql -U bookhub_user -d bookhub_db

redis-cli:
	docker-compose exec redis redis-cli

# Для быстрого тестирования
quick-test:
	docker-compose exec web python scripts/quick_test.py

# Запуск с разными профилями
dev:
	docker-compose -f docker-compose.yml up -d

prod:
	docker-compose -f docker-compose.prod.yml up -d