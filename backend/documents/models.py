from django.conf import settings
from django.db import models


class DocumentTemplate(models.Model):
    """Шаблон документа (например, docx-файл-шаблон)."""

    name = models.CharField(max_length=255)
    doc_type = models.CharField(max_length=50)
    file = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "document_templates"
        verbose_name = "Document template"
        verbose_name_plural = "Document templates"

    def __str__(self) -> str:
        return self.name


class Document(models.Model):
    """Документ по заказу (черновик/подписан и т.п.)."""

    number = models.CharField(max_length=30, unique=True)
    doc_type = models.CharField(max_length=50)
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
    counterparty_name = models.CharField(max_length=500)
    counterparty_inn = models.CharField(max_length=12)
    counterparty_address = models.TextField()
    status = models.CharField(max_length=20, default="черновик")
    docx_file = models.CharField(max_length=500, blank=True)
    pdf_file = models.CharField(max_length=500, blank=True)
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
    signed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "documents"
        verbose_name = "Document"
        verbose_name_plural = "Documents"

    def __str__(self) -> str:
        return self.number
