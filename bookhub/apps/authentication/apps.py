from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.authentication'
    verbose_name = 'Аутентификация'

    def ready(self):
        """Импортируем сигналы при запуске приложения"""
        try:
            import apps.authentication.signals  # noqa: F401
        except ImportError:
            pass