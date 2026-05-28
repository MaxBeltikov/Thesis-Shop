from django.conf import settings
from django.db import models

from .constants import DocumentStatus, DocumentType


class DocumentTemplate(models.Model):
    """Шаблон документа (docx-файл)."""

    name = models.CharField(max_length=255)
    doc_type = models.CharField(max_length=50, choices=DocumentType.choices)
    file = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "document_templates"
        verbose_name = "Document template"
        verbose_name_plural = "Document templates"

    def __str__(self) -> str:
        return self.name


class Document(models.Model):
    """Документ по заказу."""

    number = models.CharField(max_length=30, unique=True)
    doc_type = models.CharField(max_length=50, choices=DocumentType.choices)
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="documents",
    )
    template = models.ForeignKey(
        DocumentTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documents",
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
    )
    counterparty_name = models.CharField(max_length=500)
    counterparty_inn = models.CharField(max_length=12)
    counterparty_address = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=DocumentStatus.choices,
        default=DocumentStatus.DRAFT,
    )
    docx_file = models.CharField(max_length=500, blank=True)
    pdf_file = models.CharField(max_length=500, blank=True)
    responsible = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="responsible_documents",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_documents",
    )
    signed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="signed_documents",
    )
    sent_at = models.DateTimeField(null=True, blank=True)
    signed_at = models.DateTimeField(null=True, blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "documents"
        verbose_name = "Document"
        verbose_name_plural = "Documents"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.number
