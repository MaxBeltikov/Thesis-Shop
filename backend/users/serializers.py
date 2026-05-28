from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import ActionLog

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source="role.name", read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "role", "first_name", "last_name"]


class RegisterSerializer(serializers.ModelSerializer):
    """Публичная регистрация: всегда роль client (менеджеров/админов создаёт администратор)."""

    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["email", "password", "first_name", "last_name"]

    def create(self, validated_data):
        from .models import Role

        password = validated_data.pop("password")
        role_obj, _ = Role.objects.get_or_create(
            name="client",
            defaults={"description": "Client"},
        )
        validated_data["role"] = role_obj
        return User.objects.create_user(password=password, **validated_data)


class ActionLogSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = ActionLog
        fields = [
            "id",
            "user",
            "user_email",
            "action",
            "entity_type",
            "entity_id",
            "details",
            "ip_address",
            "created_at",
        ]
        read_only_fields = fields
