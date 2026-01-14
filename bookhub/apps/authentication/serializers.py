# apps/authentication/serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError
from apps.users.models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password', 'password_confirm')
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
        }

    def validate_email(self, value):
        # Проверка формата email
        try:
            validate_email(value)
        except DjangoValidationError:
            raise serializers.ValidationError(_('Invalid email format.'))

        # Проверка уникальности
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(_('User with this email already exists.'))

        return value.lower()

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError(_('User with this username already exists.'))
        return value

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        # Вместо authenticate() используем прямую проверку
        from django.contrib.auth import get_user_model
        User = get_user_model()

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(_('Invalid email or password.'))

        if not user.check_password(password):
            raise serializers.ValidationError(_('Invalid email or password.'))

        if not user.is_active:
            raise serializers.ValidationError(_('User account is disabled.'))

        data['user'] = user
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            is_verified=False  # Требуется подтверждение email
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        user = authenticate(email=email, password=password)

        if not user:
            raise serializers.ValidationError(_('Invalid email or password.'))

        if not user.is_active:
            raise serializers.ValidationError(_('User account is disabled.'))

        data['user'] = user
        return data


class TokenSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    new_password_confirm = serializers.CharField(required=True, min_length=8)

    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': _('Passwords do not match.')
            })

        if data['old_password'] == data['new_password']:
            raise serializers.ValidationError({
                'new_password': _('New password must be different from old password.')
            })

        return data


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class ConfirmResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    new_password_confirm = serializers.CharField(required=True, min_length=8)

    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': _('Passwords do not match.')
            })
        return data