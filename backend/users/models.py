from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class Role(models.Model):
    """Роль пользователя (1:1 с ER: таблица roles)."""

    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = "roles"
        verbose_name = "Role"
        verbose_name_plural = "Roles"

    def __str__(self) -> str:
        return self.name


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        # По умолчанию суперпользователь = admin.
        if not extra_fields.get("role"):
            admin_role, _ = Role.objects.get_or_create(name="admin", defaults={"description": "Admin"})
            extra_fields["role"] = admin_role
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None

    email = models.EmailField(unique=True)
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()


class ActionLog(models.Model):
    """Журнал действий пользователя (аудит)."""

    user = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="action_logs",
    )
    action = models.CharField(max_length=100)
    entity_type = models.CharField(max_length=50)
    entity_id = models.IntegerField()
    details = models.JSONField(null=True, blank=True)
    ip_address = models.CharField(max_length=45, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "action_logs"
        verbose_name = "Action log"
        verbose_name_plural = "Action logs"

    def __str__(self) -> str:
        return f"{self.action} ({self.entity_type}:{self.entity_id})"
