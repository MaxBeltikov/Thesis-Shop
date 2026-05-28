"""
Оформление документов по типовой деловой практике (ориентир — ГОСТ Р 7.0.97-2016).
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.conf import settings
from django.utils import timezone

from documents.constants import DocumentType
from documents.models import Document

MONTHS_RU = (
    "января",
    "февраля",
    "марта",
    "апреля",
    "мая",
    "июня",
    "июля",
    "августа",
    "сентября",
    "октября",
    "ноября",
    "декабря",
)

DOC_TITLES = {
    DocumentType.COMMERCIAL_PROPOSAL: "КОММЕРЧЕСКОЕ ПРЕДЛОЖЕНИЕ",
    DocumentType.INVOICE: "СЧЁТ НА ОПЛАТУ",
    DocumentType.ACT: "АКТ ВЫПОЛНЕННЫХ РАБОТ (ОКАЗАННЫХ УСЛУГ)",
    DocumentType.WAYBILL: "ТОВАРНАЯ НАКЛАДНАЯ",
}


def user_fio(user) -> str:
    """Только ФИО для документов; без email. Если не указано — пустая строка."""
    if user is None:
        return ""
    first = (user.first_name or "").strip()
    last = (user.last_name or "").strip()
    if last and first:
        return f"{last} {first}"
    if last:
        return last
    if first:
        return first
    return ""


def format_date_ru(dt=None) -> str:
    local = timezone.localtime(dt) if dt else timezone.localtime()
    d = local.date()
    return f"«{d.day:02d}» {MONTHS_RU[d.month - 1]} {d.year} г."


def format_money(value) -> str:
    n = Decimal(str(value))
    return f"{n:,.2f}".replace(",", " ").replace(".", ",")


def seller_info() -> dict:
    return {
        "name": getattr(settings, "COMPANY_NAME", 'ООО "Демо Коммерция"'),
        "inn": getattr(settings, "COMPANY_INN", "7701234567"),
        "kpp": getattr(settings, "COMPANY_KPP", "770101001"),
        "address": getattr(settings, "COMPANY_ADDRESS", "109000, г. Москва, ул. Примерная, д. 1"),
        "phone": getattr(settings, "COMPANY_PHONE", "+7 (495) 000-00-00"),
    }


def build_document_context(document: Document) -> dict:
    order = document.order
    items_qs = list(order.items.select_related("product").all())

    table_rows = []
    for idx, item in enumerate(items_qs, start=1):
        table_rows.append(
            {
                "num": idx,
                "name": item.product.name,
                "unit": item.product.unit or "шт.",
                "qty": item.quantity,
                "price": item.price,
                "amount": item.amount,
            }
        )

    responsible = document.responsible or document.created_by
    doc_type = document.doc_type

    return {
        "title": DOC_TITLES.get(doc_type, document.get_doc_type_display().upper()),
        "number": document.number,
        "date": format_date_ru(),
        "order_number": order.number,
        "doc_type": doc_type,
        "doc_type_label": document.get_doc_type_display(),
        "status": document.get_status_display(),
        "seller": seller_info(),
        "buyer": {
            "name": document.counterparty_name,
            "inn": document.counterparty_inn,
            "address": document.counterparty_address,
        },
        "items": table_rows,
        "total_amount": order.total_amount,
        "total_formatted": format_money(order.total_amount),
        "client_name": user_fio(order.client),
        "manager_name": user_fio(order.manager),
        "responsible_name": user_fio(responsible),
        "signed_by_name": user_fio(document.signed_by) if document.signed_by else "",
        "created_by_name": user_fio(document.created_by),
        "vat_note": "Без НДС (НДС не облагается).",
    }
