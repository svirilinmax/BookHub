from rest_framework import serializers

from .models import User


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_verified",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "email", "is_verified", "created_at", "updated_at"]

    def update(self, instance, validated_data):
        if "email" in validated_data:
            del validated_data["email"]

        return super().update(instance, validated_data)
