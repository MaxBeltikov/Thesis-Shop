import secrets

from django.utils import timezone
from rest_framework import serializers

from orders.models import Order
from users.permissions import is_manager_or_admin

from .constants import DocumentStatus
from .models import Document, DocumentTemplate
from .services.generation import generate_document_files


class DocumentTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentTemplate
        fields = ["id", "name", "doc_type", "file", "created_at"]
        read_only_fields = ["id", "created_at"]


class DocumentSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source="order.number", read_only=True)
    template_name = serializers.CharField(source="template.name", read_only=True, allow_null=True)
    created_by_email = serializers.EmailField(source="created_by.email", read_only=True, allow_null=True)
    signed_by_email = serializers.EmailField(source="signed_by.email", read_only=True, allow_null=True)
    responsible_email = serializers.EmailField(source="responsible.email", read_only=True, allow_null=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    doc_type_display = serializers.CharField(source="get_doc_type_display", read_only=True)
    parent_number = serializers.CharField(source="parent.number", read_only=True, allow_null=True)
    children = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            "id",
            "number",
            "doc_type",
            "doc_type_display",
            "order",
            "order_number",
            "parent",
            "parent_number",
            "children",
            "template",
            "template_name",
            "counterparty_name",
            "counterparty_inn",
            "counterparty_address",
            "status",
            "status_display",
            "docx_file",
            "pdf_file",
            "responsible",
            "responsible_email",
            "created_by",
            "created_by_email",
            "signed_by",
            "signed_by_email",
            "sent_at",
            "signed_at",
            "rejected_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_by",
            "signed_by",
            "signed_at",
            "sent_at",
            "rejected_at",
            "created_at",
            "updated_at",
            "order_number",
            "template_name",
            "created_by_email",
            "signed_by_email",
            "responsible_email",
            "status_display",
            "doc_type_display",
            "parent_number",
            "children",
            "docx_file",
            "pdf_file",
        ]
        extra_kwargs = {
            "number": {"required": False, "allow_blank": True},
            "template": {"required": False},
            "parent": {"required": False},
            "responsible": {"required": False},
        }

    def validate_order(self, value: Order):
        request = self.context.get("request")
        user = request.user if request else None
        if user and value.client_id != user.id:
            if not is_manager_or_admin(user):
                raise serializers.ValidationError("Можно создавать документы только по своим заказам.")
        return value

    def create(self, validated_data):
        request = self.context.get("request")
        if not validated_data.get("number"):
            validated_data["number"] = f"DOC-{timezone.now().strftime('%Y%m%d')}-{secrets.token_hex(4).upper()}"
        if not validated_data.get("status"):
            validated_data["status"] = DocumentStatus.DRAFT
        user = request.user if request and request.user.is_authenticated else None
        validated_data.setdefault("created_by", user)
        validated_data.setdefault("responsible", user)
        doc = Document.objects.create(**validated_data)
        # generate_document_files сохраняет пути в БД; возвращаем обновлённый экземпляр
        return generate_document_files(doc)

    def get_children(self, obj: Document):
        qs = getattr(obj, "children", None)
        if qs is None:
            qs = Document.objects.filter(parent=obj)
        else:
            qs = qs.all()
        qs = qs.order_by("created_at")
        return [
            {
                "id": d.id,
                "number": d.number,
                "doc_type": d.doc_type,
                "doc_type_display": d.get_doc_type_display(),
                "status": d.status,
                "status_display": d.get_status_display(),
            }
            for d in qs
        ]


class DocumentSignSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)

    def validate_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Неверный пароль (имитация ЭЦП).")
        return value


class DocumentRejectSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True)
