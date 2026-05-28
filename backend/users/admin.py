from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import ActionLog, Role, User


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description")
    search_fields = ("name",)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("id", "email", "role", "is_staff", "is_active", "date_joined")
    list_filter = ("is_staff", "is_active", "role")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal", {"fields": ("first_name", "last_name", "role")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser")}),
        ("Dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "role", "is_staff", "is_active"),
            },
        ),
    )


@admin.register(ActionLog)
class ActionLogAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "action", "entity_type", "entity_id", "ip_address", "created_at")
    list_filter = ("action", "entity_type", "created_at")
    search_fields = ("user__email", "action", "entity_type")
    readonly_fields = ("created_at",)
