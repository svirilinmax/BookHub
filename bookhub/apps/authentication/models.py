import uuid
from datetime import datetime, timedelta

import jwt
from apps.core.models import BaseModel
from django.conf import settings
from django.db import models
from django.utils import timezone


class AuthToken(BaseModel):
    """
    Модель для хранения JWT токенов.
    """

    TOKEN_TYPES = [
        ("access", "Access Token"),
        ("refresh", "Refresh Token"),
        ("verification", "Email Verification"),
        ("password_reset", "Password Reset"),
    ]

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="auth_tokens",
        verbose_name="Пользователь",
    )
    token_type = models.CharField(
        max_length=20, choices=TOKEN_TYPES, verbose_name="Тип токена"
    )
    token = models.TextField(verbose_name="Токен (хешированный для refresh)")
    expires_at = models.DateTimeField(verbose_name="Истекает в")
    is_blacklisted = models.BooleanField(default=False, verbose_name="В черном списке")
    ip_address = models.GenericIPAddressField(
        null=True, blank=True, verbose_name="IP адрес"
    )
    user_agent = models.TextField(blank=True, verbose_name="User Agent")

    class Meta:
        verbose_name = "Токен аутентификации"
        verbose_name_plural = "Токены аутентификации"
        indexes = [
            models.Index(fields=["user", "token_type"]),
            models.Index(fields=["expires_at"]),
            models.Index(fields=["is_blacklisted"]),
        ]

    def __str__(self):
        return f"{self.user} - {self.get_token_type_display()}"

    @property
    def is_expired(self):
        """Проверяет, истек ли срок действия токена"""
        return timezone.now() > self.expires_at

    @property
    def is_valid(self):
        """Проверяет, валиден ли токен"""
        return not self.is_expired and not self.is_blacklisted

    @classmethod
    def create_access_token(cls, user, ip=None, user_agent=""):
        """
        Создает JWT access token
        """
        payload = {
            "user_id": str(user.id),
            "email": user.email,
            "type": "access",
            "exp": datetime.utcnow()
            + timedelta(
                minutes=int(getattr(settings, "ACCESS_TOKEN_LIFETIME_MINUTES", 30))
            ),
            "iat": datetime.utcnow(),
        }

        secret_key = getattr(settings, "JWT_SECRET_KEY", settings.SECRET_KEY)
        algorithm = getattr(settings, "JWT_ALGORITHM", "HS256")

        token = jwt.encode(payload, secret_key, algorithm=algorithm)

        auth_token = cls.objects.create(
            user=user,
            token_type="access",
            token=token,
            expires_at=timezone.now()
            + timedelta(
                minutes=int(getattr(settings, "ACCESS_TOKEN_LIFETIME_MINUTES", 30))
            ),
            ip_address=ip,
            user_agent=user_agent[:500] if user_agent else "",
        )

        return auth_token, token

    @classmethod
    def create_refresh_token(cls, user, ip=None, user_agent=""):
        """
        Создает refresh token
        """
        import bcrypt

        # Генерируем случайный refresh token
        raw_token = str(uuid.uuid4()) + str(uuid.uuid4())

        # Хешируем для хранения в БД
        salt = bcrypt.gensalt()
        hashed_token = bcrypt.hashpw(raw_token.encode("utf-8"), salt)

        auth_token = cls.objects.create(
            user=user,
            token_type="refresh",
            token=hashed_token.decode("utf-8"),
            expires_at=timezone.now()
            + timedelta(days=int(getattr(settings, "REFRESH_TOKEN_LIFETIME_DAYS", 7))),
            ip_address=ip,
            user_agent=user_agent[:500] if user_agent else "",
        )

        return auth_token, raw_token

    @classmethod
    def verify_refresh_token(cls, user, raw_token):
        """
        Проверяет refresh token
        """
        import bcrypt

        # Ищем активные refresh токены пользователя
        refresh_tokens = cls.objects.filter(
            user=user,
            token_type="refresh",
            is_blacklisted=False,
            expires_at__gt=timezone.now(),
        )

        for token_obj in refresh_tokens:
            if bcrypt.checkpw(
                raw_token.encode("utf-8"), token_obj.token.encode("utf-8")
            ):
                return token_obj

        return None

    @classmethod
    def blacklist_user_tokens(cls, user):
        """
        Добавляет все токены пользователя в черный список
        """
        cls.objects.filter(user=user, is_blacklisted=False).update(is_blacklisted=True)


class Session(BaseModel):
    """
    Модель для хранения сессий
    """

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="sessions",
        verbose_name="Пользователь",
    )
    session_key = models.CharField(
        max_length=40, unique=True, verbose_name="Ключ сессии"
    )
    ip_address = models.GenericIPAddressField(verbose_name="IP адрес")
    user_agent = models.TextField(blank=True, verbose_name="User Agent")
    last_activity = models.DateTimeField(
        auto_now=True, verbose_name="Последняя активность"
    )
    expires_at = models.DateTimeField(verbose_name="Истекает в")

    class Meta:
        verbose_name = "Сессия"
        verbose_name_plural = "Сессии"
        indexes = [
            models.Index(fields=["session_key"]),
            models.Index(fields=["user", "expires_at"]),
        ]

    def __str__(self):
        return f"{self.user} - {self.session_key[:10]}..."

    @property
    def is_expired(self):
        """Проверяет, истекла ли сессия"""
        return timezone.now() > self.expires_at

    @classmethod
    def create_session(cls, user, ip, user_agent="", duration_days=30):
        """
        Создает новую сессию для пользователя
        """
        session_key = str(uuid.uuid4())

        session = cls.objects.create(
            user=user,
            session_key=session_key,
            ip_address=ip,
            user_agent=user_agent[:500] if user_agent else "",
            expires_at=timezone.now() + timedelta(days=duration_days),
        )

        return session, session_key

    @classmethod
    def get_valid_session(cls, session_key):
        """
        Получает валидную сессию по ключу
        """
        try:
            session = cls.objects.get(
                session_key=session_key, expires_at__gt=timezone.now()
            )
            return session
        except cls.DoesNotExist:
            return None


class LoginAttempt(BaseModel):
    """
    Модель для отслеживания попыток входа
    """

    email = models.EmailField(verbose_name="Email")
    ip_address = models.GenericIPAddressField(verbose_name="IP адрес")
    user_agent = models.TextField(blank=True, verbose_name="User Agent")
    success = models.BooleanField(default=False, verbose_name="Успешно")
    failure_reason = models.CharField(
        max_length=255, blank=True, verbose_name="Причина неудачи"
    )

    class Meta:
        verbose_name = "Попытка входа"
        verbose_name_plural = "Попытки входа"
        ordering = ["-created_at"]

    def __str__(self):
        status = "Yes" if self.success else "No"
        return f"{status} {self.email} - {self.created_at}"

    @classmethod
    def is_ip_blocked(cls, ip_address, max_attempts=5, block_minutes=15):
        """
        Проверка блокировки IP-адреса при превышении лимита неудачных попыток
        """
        from datetime import timedelta

        from django.utils import timezone

        recent_time = timezone.now() - timedelta(minutes=block_minutes)

        failed_attempts = cls.objects.filter(
            ip_address=ip_address, success=False, created_at__gt=recent_time
        ).count()

        return failed_attempts >= max_attempts


class EmailVerificationToken(BaseModel):
    """Токен для подтверждения email"""

    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="email_verification_tokens"
    )
    token = models.CharField(max_length=100, unique=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Токен подтверждения email"
        verbose_name_plural = "Токены подтверждения email"

    def __str__(self):
        return f"{self.user.email} - {self.token[:10]}..."

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @property
    def is_valid(self):
        return not self.is_expired and not self.is_used


class PasswordResetToken(BaseModel):
    """Токен для сброса пароля"""

    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="password_reset_tokens"
    )
    token = models.CharField(max_length=100, unique=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Токен сброса пароля"
        verbose_name_plural = "Токены сброса пароля"

    def __str__(self):
        return f"{self.user.email} - {self.token[:10]}..."

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @property
    def is_valid(self):
        return not self.is_expired and not self.is_used
