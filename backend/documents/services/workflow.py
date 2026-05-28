"""Бизнес-процессы: цепочка КП -> счёт -> акт, автоматический акт при завершении заказа."""

from __future__ import annotations

import secrets

from django.utils import timezone

from documents.constants import DOCUMENT_CHAIN, DocumentStatus, DocumentType
from documents.models import Document
from documents.services.generation import generate_document_files
from orders.models import Order


def _new_document_number(prefix: str) -> str:
    return f"{prefix}-{timezone.now().strftime('%Y%m%d')}-{secrets.token_hex(4).upper()}"


def create_next_document_in_chain(
    source: Document,
    user,
    *,
    generate_files: bool = True,
) -> Document | None:
    """Создаёт следующий документ в цепочке (КП -> счёт -> акт).

    Модель A: для каждого документа допускается только один следующий этап.
    Если следующий документ уже создан, возвращает его (не создаёт дубликат).
    """
    next_type = DOCUMENT_CHAIN.get(source.doc_type)
    if not next_type:
        return None

    existing = (
        Document.objects.filter(parent=source, doc_type=next_type)
        .order_by("-created_at")
        .first()
    )
    if existing:
        return existing

    child = Document.objects.create(
        number=_new_document_number(next_type.upper()[:3]),
        doc_type=next_type,
        order=source.order,
        template=source.template,
        parent=source,
        counterparty_name=source.counterparty_name,
        counterparty_inn=source.counterparty_inn,
        counterparty_address=source.counterparty_address,
        status=DocumentStatus.DRAFT,
        created_by=user,
        responsible=user,
    )
    if generate_files:
        generate_document_files(child)
    return child


def auto_create_act_for_order(order: Order, user) -> Document | None:
    """При выполнении заказа создаёт акт, если его ещё нет."""
    if Document.objects.filter(order=order, doc_type=DocumentType.ACT).exists():
        return None

    invoice = (
        Document.objects.filter(order=order, doc_type=DocumentType.INVOICE)
        .order_by("-created_at")
        .first()
    )
    source = invoice
    if source is None:
        cp = (
            Document.objects.filter(order=order, doc_type=DocumentType.COMMERCIAL_PROPOSAL)
            .order_by("-created_at")
            .first()
        )
        source = cp

    counterparty_name = "Контрагент"
    counterparty_inn = "0000000000"
    counterparty_address = "—"
    parent = None
    if source:
        counterparty_name = source.counterparty_name
        counterparty_inn = source.counterparty_inn
        counterparty_address = source.counterparty_address
        parent = source

    act = Document.objects.create(
        number=_new_document_number("ACT"),
        doc_type=DocumentType.ACT,
        order=order,
        parent=parent,
        counterparty_name=counterparty_name,
        counterparty_inn=counterparty_inn,
        counterparty_address=counterparty_address,
        status=DocumentStatus.DRAFT,
        created_by=user,
        responsible=user,
    )
    generate_document_files(act)
    return act


ORDER_COMPLETED_STATUSES = {"выполнен", "completed", "завершён", "done"}
