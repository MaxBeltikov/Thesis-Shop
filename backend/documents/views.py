from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from users.audit import log_action
from users.permissions import IsDocumentOrderParticipantOrManager, IsManagerOrAdminOrReadOnly

from .constants import DocumentStatus
from .constants import DOCUMENT_CHAIN
from .models import Document, DocumentTemplate
from .serializers import (
    DocumentRejectSerializer,
    DocumentSerializer,
    DocumentSignSerializer,
    DocumentTemplateSerializer,
)
from .services.generation import generate_document_files
from .services.workflow import create_next_document_in_chain


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
        qs = Document.objects.select_related(
            "order", "template", "created_by", "signed_by", "responsible", "parent"
        ).prefetch_related("children")
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

    @action(detail=True, methods=["post"], url_path="generate")
    def generate(self, request, pk=None):
        """Перегенерировать docx/pdf."""
        document = self.get_object()
        generate_document_files(document)
        log_action(request.user, "generate", "document", document.pk, request)
        return Response(DocumentSerializer(document, context={"request": request}).data)

    @action(detail=True, methods=["post"], url_path="send")
    def send(self, request, pk=None):
        """Отправить документ (статус «отправлен»)."""
        document = self.get_object()
        if document.status == DocumentStatus.SIGNED:
            return Response(
                {"detail": "Подписанный документ нельзя отправить повторно."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if document.status == DocumentStatus.REJECTED:
            return Response(
                {"detail": "Отклонённый документ нельзя отправить."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        document.status = DocumentStatus.SENT
        document.sent_at = timezone.now()
        document.save(update_fields=["status", "sent_at", "updated_at"])
        log_action(request.user, "send", "document", document.pk, request)
        return Response(DocumentSerializer(document, context={"request": request}).data)

    @action(detail=True, methods=["post"], url_path="sign")
    def sign(self, request, pk=None):
        """Подписать документ (имитация ЭЦП: проверка пароля пользователя)."""
        document = self.get_object()
        if document.status == DocumentStatus.SIGNED:
            return Response({"detail": "Документ уже подписан."}, status=status.HTTP_400_BAD_REQUEST)
        if document.status == DocumentStatus.REJECTED:
            return Response({"detail": "Отклонённый документ нельзя подписать."}, status=status.HTTP_400_BAD_REQUEST)

        ser = DocumentSignSerializer(data=request.data, context={"request": request})
        ser.is_valid(raise_exception=True)

        document.status = DocumentStatus.SIGNED
        document.signed_by = request.user
        document.signed_at = timezone.now()
        document.save(update_fields=["status", "signed_by", "signed_at", "updated_at"])
        log_action(
            request.user,
            "sign",
            "document",
            document.pk,
            request,
            details={"method": "password_ecp_simulation"},
        )
        return Response(DocumentSerializer(document, context={"request": request}).data)

    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, pk=None):
        document = self.get_object()
        ser = DocumentRejectSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        document.status = DocumentStatus.REJECTED
        document.rejected_at = timezone.now()
        document.save(update_fields=["status", "rejected_at", "updated_at"])
        log_action(
            request.user,
            "reject",
            "document",
            document.pk,
            request,
            details={"reason": ser.validated_data.get("reason", "")},
        )
        return Response(DocumentSerializer(document, context={"request": request}).data)

    @action(detail=True, methods=["post"], url_path="create-next")
    def create_next(self, request, pk=None):
        """Следующий документ в цепочке: КП -> счёт -> акт."""
        document = self.get_object()
        next_type = DOCUMENT_CHAIN.get(document.doc_type)
        if not next_type:
            return Response(
                {"detail": "Для этого типа документа нет следующего этапа цепочки."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        existing = (
            Document.objects.filter(parent=document, doc_type=next_type)
            .order_by("-created_at")
            .first()
        )
        if existing:
            log_action(
                request.user,
                "create_next",
                "document",
                existing.pk,
                request,
                details={"parent_id": document.pk, "returned_existing": True},
            )
            return Response(
                DocumentSerializer(existing, context={"request": request}).data,
                status=status.HTTP_200_OK,
            )

        child = create_next_document_in_chain(document, request.user)
        if child is None:
            return Response(
                {"detail": "Для этого типа документа нет следующего этапа цепочки."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        log_action(
            request.user,
            "create_next",
            "document",
            child.pk,
            request,
            details={"parent_id": document.pk, "returned_existing": False},
        )
        return Response(
            DocumentSerializer(child, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )
