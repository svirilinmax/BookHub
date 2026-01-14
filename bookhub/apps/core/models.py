import uuid
from django.db import models


class TimeStampedModel(models.Model):
    """Абстрактная модель с временными метками"""
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="Удалено")

    class Meta:
        abstract = True


class UUIDModel(models.Model):
    """Абстрактная модель с UUID в качестве первичного ключа"""
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        auto_created=True
    )

    class Meta:
        abstract = True


class BaseModel(TimeStampedModel, UUIDModel):
    """Базовая модель для всех моделей проекта"""

    class Meta:
        abstract = True