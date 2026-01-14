# apps/authentication/middleware.py
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
import json


class JWTAuthenticationMiddleware(MiddlewareMixin):
    """
    Middleware для определения публичных маршрутов и обработки ошибок аутентификации
    """

    # Публичные маршруты (не требуют аутентификации)
    PUBLIC_PATHS = [
        '/',
        '/api/auth/register/',
        '/api/auth/login/',
        '/api/auth/refresh/',
        '/api/auth/test/',
        '/api/auth/reset-password/',
        '/api/auth/confirm-reset-password/',
        '/api/auth/verify-email/',
        '/swagger/',
        '/redoc/',
        '/admin/',
        '/admin/login/',
        '/admin/logout/',
    ]

    # Префиксы публичных маршрутов (GET запросы)
    PUBLIC_GET_PREFIXES = [
        '/api/products/',  # Просмотр товаров - публичный
    ]

    def process_request(self, request):
        """
        Определяем, является ли маршрут публичным
        """
        # Проверяем публичные маршруты
        if self._is_public_path(request.path, request.method):
            # Для публичных маршрутов не требуется аутентификация
            return None

        # Для защищенных маршрутов аутентификацию выполнит DRF
        return None

    def _is_public_path(self, path, method):
        """
        Проверяет, является ли путь публичным
        """
        # Абсолютные совпадения
        if path in self.PUBLIC_PATHS:
            return True

        # GET запросы к определенным префиксам
        if method == 'GET':
            for prefix in self.PUBLIC_GET_PREFIXES:
                if path.startswith(prefix):
                    return True

        # API аутентификации (кроме защищенных методов)
        if path.startswith('/api/auth/'):
            protected_auth_paths = [
                '/api/auth/logout/',
                '/api/auth/change-password/',
                '/api/auth/profile/',
            ]
            return path not in protected_auth_paths

        return False

    def process_response(self, request, response):
        """
        Обработка ошибок аутентификации и авторизации
        """
        # Обрабатываем только JSON ответы
        if response.get('Content-Type', '').startswith('application/json'):
            try:
                # Для 401 ошибок (аутентификация)
                if response.status_code == 401:
                    data = json.loads(response.content)
                    if 'detail' in data and data['detail'] == 'Authentication credentials were not provided.':
                        return JsonResponse(
                            {'error': 'Authentication required. Please provide a valid JWT token.'},
                            status=401
                        )

                # Для 403 ошибок (авторизация)
                elif response.status_code == 403:
                    data = json.loads(response.content)
                    if 'detail' in data and data['detail'] == 'You do not have permission to perform this action.':
                        return JsonResponse(
                            {'error': 'Permission denied. You do not have access to this resource.'},
                            status=403
                        )
            except:
                pass  # В случае ошибки оставляем оригинальный ответ

        return response