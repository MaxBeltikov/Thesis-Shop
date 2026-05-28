from django.db import models


class DocumentStatus(models.TextChoices):
    DRAFT = "черновик", "Черновик"
    SENT = "отправлен", "Отправлен"
    SIGNED = "подписан", "Подписан"
    REJECTED = "отклонён", "Отклонён"


class DocumentType(models.TextChoices):
    COMMERCIAL_PROPOSAL = "кп", "Коммерческое предложение"
    INVOICE = "счёт", "Счёт"
    ACT = "акт", "Акт"
    WAYBILL = "накладная", "Накладная"


# Цепочка документооборота: КП -> счёт -> акт
DOCUMENT_CHAIN = {
    DocumentType.COMMERCIAL_PROPOSAL: DocumentType.INVOICE,
    DocumentType.INVOICE: DocumentType.ACT,
}
