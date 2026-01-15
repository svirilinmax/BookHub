from datetime import datetime, timedelta

import jwt
from apps.core.models import BaseModel
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    email = models.EmailField(unique=True, verbose_name="Email адрес")
    username = models.CharField(
        max_length=150, unique=True, verbose_name="Имя пользователя"
    )
    first_name = models.CharField(max_length=150, blank=True, verbose_name="Имя")
    last_name = models.CharField(max_length=150, blank=True, verbose_name="Фамилия")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    is_staff = models.BooleanField(default=False, verbose_name="Доступ к админке")
    is_verified = models.BooleanField(default=False, verbose_name="Email подтвержден")

    roles = models.ManyToManyField(
        "authorization.Role",
        through="authorization.UserRole",
        related_name="users",
        verbose_name="Роли",
    )

    email_verification_token = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Токен подтверждения email"
    )
    email_verification_sent_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Дата отправки подтверждения"
    )
    password_reset_token = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Токен сброса пароля"
    )
    password_reset_expires = models.DateTimeField(
        null=True, blank=True, verbose_name="Срок действия токена сброса"
    )

    # Для мягкого удаления (soft delete)
    deleted_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Дата удаления"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["-created_at"]
        app_label = "users"

    def __str__(self):
        return f"{self.email} ({self.username})"

    def create_jwt_token(self, token_type="access", **kwargs):
        """
        Создает JWT токен
        """
        payload = {
            "user_id": str(self.id),
            "email": self.email,
            "type": token_type,
            "exp": datetime.utcnow() + kwargs.get("lifetime", timedelta(minutes=30)),
            "iat": datetime.utcnow(),
        }

        payload.update(kwargs.get("extra_payload", {}))

        secret_key = getattr(settings, "JWT_SECRET_KEY", settings.SECRET_KEY)
        algorithm = getattr(settings, "JWT_ALGORITHM", "HS256")

        return jwt.encode(payload, secret_key, algorithm=algorithm)

    @staticmethod
    def verify_jwt_token(token):
        """
        Верифицирует JWT токен
        """
        import jwt
        from django.conf import settings
        from django.core.exceptions import ValidationError as DjangoValidationError

        try:
            secret_key = getattr(settings, "JWT_SECRET_KEY", settings.SECRET_KEY)
            algorithm = getattr(settings, "JWT_ALGORITHM", "HS256")

            payload = jwt.decode(
                token,
                secret_key,
                algorithms=[algorithm],
                options={"require": ["exp", "iat", "user_id"]},
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise DjangoValidationError("Token has expired")
        except jwt.InvalidTokenError:
            raise DjangoValidationError("Invalid token")
