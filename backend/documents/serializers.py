import secrets

from django.utils import timezone
from rest_framework import serializers

from orders.models import Order
from users.permissions import is_manager_or_admin

from .models import Document, DocumentTemplate


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

    class Meta:
        model = Document
        fields = [
            "id",
            "number",
            "doc_type",
            "order",
            "order_number",
            "template",
            "template_name",
            "counterparty_name",
            "counterparty_inn",
            "counterparty_address",
            "status",
            "docx_file",
            "pdf_file",
            "created_by",
            "created_by_email",
            "signed_by",
            "signed_by_email",
            "signed_at",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_by",
            "signed_by",
            "signed_at",
            "created_at",
            "order_number",
            "template_name",
            "created_by_email",
            "signed_by_email",
        ]

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
        doc = Document.objects.create(
            **validated_data,
            created_by=request.user if request and request.user.is_authenticated else None,
        )
        return doc
