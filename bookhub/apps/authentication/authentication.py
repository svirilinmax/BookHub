import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

User = get_user_model()


class JWTAuthentication(BaseAuthentication):
    """
    Аутентификация по JWT токену
    """

    def authenticate(self, request):
        # Получаем заголовок Authorization
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            # Нет токена - анонимный пользователь
            return None

        token = auth_header.split(" ")[1]

        try:
            # Верифицируем токен
            secret_key = getattr(settings, "JWT_SECRET_KEY", settings.SECRET_KEY)
            algorithm = getattr(settings, "JWT_ALGORITHM", "HS256")

            payload = jwt.decode(
                token,
                secret_key,
                algorithms=[algorithm],
                options={"require": ["exp", "iat", "user_id"]},
            )

            if payload.get("type") != "access":
                raise AuthenticationFailed("Invalid token type. Access token required.")

            # Получаем пользователя
            user = User.objects.get(id=payload["user_id"], is_active=True)

            # Обновляем время последнего входа
            user.last_login = timezone.now()
            user.save(update_fields=["last_login"])

            return (user, token)

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token has expired")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid token")
        except User.DoesNotExist:
            raise AuthenticationFailed("User not found or inactive")
        except Exception as e:
            raise AuthenticationFailed(str(e))

    def authenticate_header(self, request):
        return "Bearer"
