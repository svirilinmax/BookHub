FROM python:3.11-slim

WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    libpq-dev \
    curl \
    redis-tools \
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код проекта
COPY ./bookhub ./bookhub
COPY entrypoint.sh .

# Создаем пользователя (опционально)
RUN useradd -m -u 1000 django
RUN chown -R django:django /app
USER django

# Рабочая директория внутри контейнера
WORKDIR /app/bookhub

EXPOSE 8000

CMD ["../entrypoint.sh"]
