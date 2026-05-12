from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source="role.name", read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "role"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    # Принимаем роль как строку (client/manager/admin), а не pk.
    role = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ["email", "password", "role", "first_name", "last_name"]

    def create(self, validated_data):
        from .models import Role

        password = validated_data.pop("password")
        role_name = (validated_data.pop("role", "") or "client").strip().lower()
        role_obj, _ = Role.objects.get_or_create(
            name=role_name,
            defaults={"description": role_name.capitalize()},
        )
        validated_data["role"] = role_obj
        return User.objects.create_user(password=password, **validated_data)
