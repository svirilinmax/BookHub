FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    libpq-dev \
    curl \
    redis-tools \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./bookhub ./bookhub
COPY entrypoint.sh .

RUN useradd -m -u 1000 django
RUN chown -R django:django /app
USER django

WORKDIR /app/bookhub

EXPOSE 8000

CMD ["../entrypoint.sh"]
