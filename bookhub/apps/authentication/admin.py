from django.contrib import admin

from .models import AuthToken, LoginAttempt, Session


@admin.register(AuthToken)
class AuthTokenAdmin(admin.ModelAdmin):
    """Администрирование JWT-токенов"""

    list_display = (
        "user",
        "token_type",
        "is_expired",
        "is_blacklisted",
        "created_at",
        "expires_at",
    )
    list_filter = ("token_type", "is_blacklisted", "created_at")
    search_fields = ("user__email", "user__username", "ip_address")
    readonly_fields = ("created_at", "updated_at", "expires_at", "is_expired")
    ordering = ("-created_at",)

    def is_expired(self, obj):
        return obj.is_expired

    is_expired.boolean = True
    is_expired.short_description = "Истек"

    fieldsets = (
        ("Основная информация", {"fields": ("user", "token_type", "is_blacklisted")}),
        ("Детали токена", {"fields": ("token", "expires_at", "is_expired")}),
        ("Информация о запросе", {"fields": ("ip_address", "user_agent")}),
        ("Временные метки", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    """Администрирование сессий"""

    list_display = (
        "user",
        "session_key_short",
        "ip_address",
        "last_activity",
        "is_expired",
    )
    list_filter = ("last_activity", "created_at")
    search_fields = ("user__email", "user__username", "session_key", "ip_address")
    readonly_fields = ("created_at", "updated_at", "last_activity", "is_expired")
    ordering = ("-last_activity",)

    def session_key_short(self, obj):
        return f"{obj.session_key[:15]}..."

    session_key_short.short_description = "Ключ сессии"

    def is_expired(self, obj):
        return obj.is_expired

    is_expired.boolean = True
    is_expired.short_description = "Истекла"

    fieldsets = (
        ("Основная информация", {"fields": ("user", "session_key")}),
        ("Информация о подключении", {"fields": ("ip_address", "user_agent")}),
        ("Статус", {"fields": ("last_activity", "expires_at", "is_expired")}),
        ("Временные метки", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    """Мониторинг попыток входа"""

    list_display = ("email", "ip_address", "success", "failure_reason", "created_at")
    list_filter = ("success", "created_at")
    search_fields = ("email", "ip_address", "failure_reason")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)

    fieldsets = (
        ("Основная информация", {"fields": ("email", "ip_address", "success")}),
        ("Детали попытки", {"fields": ("failure_reason", "user_agent")}),
        ("Временные метки", {"fields": ("created_at", "updated_at")}),
    )
