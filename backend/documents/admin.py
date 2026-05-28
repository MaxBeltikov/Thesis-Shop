from django.contrib import admin

from .models import Document, DocumentTemplate


@admin.register(DocumentTemplate)
class DocumentTemplateAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "doc_type", "created_at")
    list_filter = ("doc_type",)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "number",
        "doc_type",
        "order",
        "status",
        "responsible",
        "created_at",
        "signed_at",
    )
    list_filter = ("doc_type", "status", "created_at")
    search_fields = ("number", "counterparty_name", "order__number")
    raw_id_fields = ("order", "template", "parent", "created_by", "signed_by", "responsible")
