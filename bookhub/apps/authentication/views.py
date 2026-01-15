import uuid

from apps.authentication.authentication import JWTAuthentication
from apps.authentication.models import (
    AuthToken,
    EmailVerificationToken,
    LoginAttempt,
    PasswordResetToken,
)
from apps.users.models import User
from django.core.cache import cache
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    ChangePasswordSerializer,
    ConfirmResetPasswordSerializer,
    LoginSerializer,
    RegisterSerializer,
    ResetPasswordSerializer,
)


class RegisterView(generics.CreateAPIView):
    """
    Регистрация нового пользователя
    """

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Создаем токен подтверждения
        verification_token = str(uuid.uuid4())
        expires_at = timezone.now() + timezone.timedelta(hours=24)

        EmailVerificationToken.objects.create(
            user=user, token=verification_token, expires_at=expires_at
        )

        print("\n" + "=" * 60)
        print("EMAIL VERIFICATION (FOR LOCALHOST)")
        print("=" * 60)
        print(f"To: {user.email}")
        print("Verification link:")
        base_url_verify = "http://localhost:8000/api/auth/verify-email/"
        print(f"{base_url_verify}?token={verification_token}")
        print("=" * 60 + "\n")

        access_token = user.create_jwt_token(
            token_type="access", lifetime=timezone.timedelta(minutes=30)
        )

        # Создаем refresh токен
        refresh_token_obj, raw_refresh_token = AuthToken.create_refresh_token(
            user=user,
            ip=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )

        return Response(
            {
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "is_verified": user.is_verified,
                },
                "tokens": {"access": access_token, "refresh": raw_refresh_token},
                "message": "Registration successful! "
                "Please confirm your email "
                "(link is in the server console).",
                "verification_info": "For testing: "
                "check server console for verification link",
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """
    Вход пользователя
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        ip_address = request.META.get("REMOTE_ADDR")
        user_agent = request.META.get("HTTP_USER_AGENT", "")

        # Проверяем защиту от брутфорса
        if LoginAttempt.is_ip_blocked(ip_address):
            LoginAttempt.objects.create(
                email=serializer.validated_data["email"],
                ip_address=ip_address,
                user_agent=user_agent,
                success=False,
                failure_reason="IP blocked due to too many failed attempts",
            )
            return Response(
                {"error": "Too many failed attempts. " "Please try again later."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        # Создаем запись о попытке входа
        login_attempt = LoginAttempt.objects.create(
            email=serializer.validated_data["email"],
            ip_address=ip_address,
            user_agent=user_agent,
            success=True,
        )

        # Создаем access токен
        access_token = user.create_jwt_token(
            token_type="access", lifetime=timezone.timedelta(minutes=30)
        )

        # Создаем refresh токен
        refresh_token_obj, raw_refresh_token = AuthToken.create_refresh_token(
            user=user, ip=ip_address, user_agent=user_agent
        )

        # Обновляем last_login
        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])

        login_attempt.save()

        return Response(
            {
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "is_verified": user.is_verified,
                },
                "tokens": {"access": access_token, "refresh": raw_refresh_token},
            }
        )


class LogoutView(APIView):
    """
    Выход пользователя
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Добавляем все токены пользователя в черный список
        AuthToken.blacklist_user_tokens(request.user)

        # Очищаем кеш сессий
        cache.delete_pattern(f"session_{request.user.id}_*")

        return Response({"message": "Successfully logged out"})


class RefreshTokenView(APIView):
    """
    Обновление access токена с помощью refresh токена
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {"error": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Ищем валидный refresh токен
        for token_obj in AuthToken.objects.filter(
            token_type="refresh", is_blacklisted=False, expires_at__gt=timezone.now()
        ):
            import bcrypt

            if bcrypt.checkpw(
                refresh_token.encode("utf-8"), token_obj.token.encode("utf-8")
            ):
                # Нашли валидный токен, создаем новый access токен
                new_access_token = token_obj.user.create_jwt_token(
                    token_type="access", lifetime=timezone.timedelta(minutes=30)
                )

                # Помечаем старый refresh токен как использованный
                token_obj.is_blacklisted = True
                token_obj.save()

                # Создаем новый refresh токен
                (
                    new_refresh_token_obj,
                    raw_refresh_token,
                ) = AuthToken.create_refresh_token(
                    user=token_obj.user,
                    ip=request.META.get("REMOTE_ADDR"),
                    user_agent=request.META.get("HTTP_USER_AGENT", ""),
                )

                return Response(
                    {"access": new_access_token, "refresh": raw_refresh_token}
                )

        return Response(
            {"error": "Invalid or expired refresh token"},
            status=status.HTTP_401_UNAUTHORIZED,
        )


class ChangePasswordView(APIView):
    """
    Смена пароля авторизованным пользователем
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user

        # Проверяем старый пароль
        if not user.check_password(serializer.validated_data["old_password"]):
            return Response(
                {"error": "Current password is incorrect"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Устанавливаем новый пароль
        user.set_password(serializer.validated_data["new_password"])
        user.save()

        AuthToken.blacklist_user_tokens(user)

        return Response(
            {"message": "Password changed successfully. Please login again."}
        )


class ResetPasswordView(APIView):
    """
    Запрос на сброс пароля
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email, is_active=True)
        except User.DoesNotExist:
            return Response(
                {
                    "message": "If an account exists with this email, "
                    "you will receive a password reset link."
                }
            )

        # Создаем токен сброса пароля
        reset_token = str(uuid.uuid4())
        expires_at = timezone.now() + timezone.timedelta(hours=1)

        PasswordResetToken.objects.create(
            user=user, token=reset_token, expires_at=expires_at
        )

        print("\n" + "=" * 60)
        print("PASSWORD RESET (FOR LOCALHOST)")
        print("=" * 60)
        print(f"To: {user.email}")
        base_url_reset = "http://localhost:8000/reset-password"
        print(f"Reset link: {base_url_reset}?token={reset_token}")
        print("=" * 60 + "\n")

        return Response(
            {
                "message": "If an account exists with this email, "
                "you will receive a password reset link.",
                "debug_info": f"Token for local testing: {reset_token}",
            }
        )


class ConfirmResetPasswordView(APIView):
    """
    Подтверждение сброса пароля
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ConfirmResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["new_password"]

        try:
            # Ищем валидный токен
            reset_token = PasswordResetToken.objects.get(
                token=token, is_used=False, expires_at__gt=timezone.now()
            )

            # Помечаем как использованный
            reset_token.is_used = True
            reset_token.save()

            # Устанавливаем новый пароль
            user = reset_token.user
            user.set_password(new_password)
            user.save()

            # Инвалидируем все существующие токены пользователя
            AuthToken.blacklist_user_tokens(user)

            return Response(
                {
                    "message": "Password reset successful! "
                    "You can now login with your new password.",
                    "email": user.email,
                }
            )

        except PasswordResetToken.DoesNotExist:
            return Response(
                {"error": "Invalid, expired or already used reset token"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class VerifyEmailView(APIView):
    """
    Подтверждение email по токену
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        token = request.GET.get("token")

        if not token:
            return Response(
                {"error": "Token is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Ищем валидный токен
            verification_token = EmailVerificationToken.objects.get(
                token=token, is_used=False, expires_at__gt=timezone.now()
            )

            # Помечаем как использованный
            verification_token.is_used = True
            verification_token.save()

            # Активируем пользователя
            user = verification_token.user
            user.is_verified = True
            user.save()

            return Response(
                {
                    "message": "Email verified successfully!",
                    "email": user.email,
                    "is_verified": user.is_verified,
                }
            )

        except EmailVerificationToken.DoesNotExist:
            return Response(
                {"error": "Invalid, expired or already used verification token"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    Получение и обновление профиля пользователя
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        from apps.users.serializers import UserProfileSerializer

        return UserProfileSerializer

    def get_object(self):
        return self.request.user


class TestView(APIView):
    """
    Простой тестовый endpoint для проверки работы
    """

    permission_classes = [AllowAny]

    def get(self, request):
        return Response(
            {
                "message": "Authentication app is working!",
                "timestamp": timezone.now(),
                "user": str(request.user)
                if request.user.is_authenticated
                else "Anonymous",
            }
        )
