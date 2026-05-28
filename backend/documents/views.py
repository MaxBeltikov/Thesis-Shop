from rest_framework import viewsets

from users.audit import log_action
from users.permissions import IsDocumentOrderParticipantOrManager, IsManagerOrAdminOrReadOnly

from .models import Document, DocumentTemplate
from .serializers import DocumentSerializer, DocumentTemplateSerializer


class DocumentTemplateViewSet(viewsets.ModelViewSet):
    queryset = DocumentTemplate.objects.all().order_by("-created_at")
    serializer_class = DocumentTemplateSerializer
    permission_classes = [IsManagerOrAdminOrReadOnly]

    def perform_create(self, serializer):
        instance = serializer.save()
        log_action(self.request.user, "create", "document_template", instance.pk, self.request)

    def perform_update(self, serializer):
        instance = serializer.save()
        log_action(self.request.user, "update", "document_template", instance.pk, self.request)

    def perform_destroy(self, instance):
        pk = instance.pk
        instance.delete()
        log_action(self.request.user, "delete", "document_template", pk, self.request)


class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = [IsDocumentOrderParticipantOrManager]

    def get_queryset(self):
        qs = Document.objects.select_related("order", "template", "created_by", "signed_by")
        user = self.request.user
        if user.is_superuser:
            return qs.order_by("-created_at")
        role = getattr(user, "role", None)
        name = (role.name or "").lower() if role else ""
        if name in ("admin", "manager"):
            return qs.order_by("-created_at")
        return qs.filter(order__client=user).order_by("-created_at")

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx

    def perform_create(self, serializer):
        instance = serializer.save()
        log_action(self.request.user, "create", "document", instance.pk, self.request)

    def perform_update(self, serializer):
        instance = serializer.save()
        log_action(self.request.user, "update", "document", instance.pk, self.request)

    def perform_destroy(self, instance):
        pk = instance.pk
        instance.delete()
        log_action(self.request.user, "delete", "document", pk, self.request)
