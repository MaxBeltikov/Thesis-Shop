from rest_framework import viewsets

from users.audit import log_action
from users.permissions import IsOrderParticipantOrManager

from .models import Order
from .serializers import OrderSerializer


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsOrderParticipantOrManager]

    def get_queryset(self):
        qs = Order.objects.select_related("client", "manager").prefetch_related("items__product")
        user = self.request.user
        if user.is_superuser:
            return qs.order_by("-created_at")
        role = getattr(user, "role", None)
        name = (role.name or "").lower() if role else ""
        if name in ("admin", "manager"):
            return qs.order_by("-created_at")
        return qs.filter(client=user).order_by("-created_at")

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx

    def perform_create(self, serializer):
        instance = serializer.save()
        log_action(self.request.user, "create", "order", instance.pk, self.request)

    def perform_update(self, serializer):
        instance = serializer.save()
        log_action(self.request.user, "update", "order", instance.pk, self.request)

    def perform_destroy(self, instance):
        pk = instance.pk
        instance.delete()
        log_action(self.request.user, "delete", "order", pk, self.request)
