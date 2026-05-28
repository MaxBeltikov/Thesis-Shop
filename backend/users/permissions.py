from rest_framework import permissions


def user_role_name(user) -> str:
    if not user or not user.is_authenticated:
        return ""
    if user.is_superuser:
        return "admin"
    role = getattr(user, "role", None)
    if role is None:
        return ""
    return (role.name or "").lower()


def is_admin(user) -> bool:
    return bool(user and user.is_authenticated and (user.is_superuser or user_role_name(user) == "admin"))


def is_manager_or_admin(user) -> bool:
    return is_admin(user) or user_role_name(user) == "manager"


class IsManagerOrAdmin(permissions.BasePermission):
    """Полный доступ к операциям записи для менеджера и администратора."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and is_manager_or_admin(request.user))


class IsAdminRole(permissions.BasePermission):
    def has_permission(self, request, view):
        return is_admin(request.user)


class IsManagerOrAdminOrReadOnly(permissions.BasePermission):
    """Чтение — любой аутентифицированный; запись — менеджер или админ."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return is_manager_or_admin(request.user)


class IsOrderParticipantOrManager(permissions.BasePermission):
    """Заказ: клиент — только свой; менеджер/админ — любой."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if is_manager_or_admin(request.user):
            return True
        return obj.client_id == request.user.id


class IsDocumentOrderParticipantOrManager(permissions.BasePermission):
    """Документ: доступ по заказу (клиент заказа или менеджер/админ)."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if is_manager_or_admin(request.user):
            return True
        return obj.order.client_id == request.user.id
