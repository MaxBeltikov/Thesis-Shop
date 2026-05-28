from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from documents.serializers import DocumentSerializer
from users.audit import log_action
from users.permissions import IsOrderParticipantOrManager

from .models import Order
from .serializers import OrderSerializer


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsOrderParticipantOrManager]
    filter_backends = [filters.SearchFilter]
    search_fields = ["number", "status", "client__email", "manager__email"]

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

    @action(detail=True, methods=["get"], url_path="documents")
    def documents(self, request, pk=None):
        """GET /api/orders/{id}/documents/ — документы заказа."""
        order = self.get_object()
        docs = order.documents.select_related(
            "template", "created_by", "signed_by", "responsible", "parent"
        ).order_by("-created_at")
        serializer = DocumentSerializer(docs, many=True, context={"request": request})
        return Response(serializer.data)
