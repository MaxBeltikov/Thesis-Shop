"""Демо-данные для презентации и ручного тестирования."""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from catalog.models import Product
from documents.constants import DocumentStatus, DocumentType
from documents.models import Document
from documents.services.generation import generate_document_files
from orders.models import Order, OrderItem
from users.models import Role

User = get_user_model()


class Command(BaseCommand):
    help = "Загрузить демо-данные (роли, пользователи, товары, заказ, документы)"

    def handle(self, *args, **options):
        client_role, _ = Role.objects.get_or_create(name="client", defaults={"description": "Клиент"})
        manager_role, _ = Role.objects.get_or_create(name="manager", defaults={"description": "Менеджер"})
        Role.objects.get_or_create(name="admin", defaults={"description": "Администратор"})

        client, _ = User.objects.get_or_create(
            email="demo.client@example.com",
            defaults={"role": client_role, "first_name": "Иван", "last_name": "Клиент"},
        )
        if not client.has_usable_password():
            client.set_password("demo1234")
            client.save()

        manager, _ = User.objects.get_or_create(
            email="demo.manager@example.com",
            defaults={"role": manager_role, "first_name": "Мария", "last_name": "Менеджер"},
        )
        if not manager.has_usable_password():
            manager.set_password("demo1234")
            manager.save()

        product, _ = Product.objects.get_or_create(
            name="Консультация (1 час)",
            defaults={
                "description": "Услуга консультации",
                "price": Decimal("2500.00"),
                "unit": "час",
                "is_active": True,
            },
        )

        order, created = Order.objects.get_or_create(
            number="ORD-DEMO-001",
            defaults={
                "client": client,
                "manager": manager,
                "status": "новый",
                "total_amount": Decimal("5000.00"),
            },
        )
        if created:
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=Decimal("2"),
                price=Decimal("2500.00"),
                amount=Decimal("5000.00"),
            )

        if not Document.objects.filter(order=order, doc_type=DocumentType.COMMERCIAL_PROPOSAL).exists():
            cp = Document.objects.create(
                number="CP-DEMO-001",
                doc_type=DocumentType.COMMERCIAL_PROPOSAL,
                order=order,
                counterparty_name='ООО "Демо"',
                counterparty_inn="7701234567",
                counterparty_address="г. Москва, ул. Примерная, 1",
                status=DocumentStatus.DRAFT,
                created_by=manager,
                responsible=manager,
            )
            generate_document_files(cp)

        self.stdout.write(self.style.SUCCESS("Демо-данные загружены."))
        self.stdout.write("  client: demo.client@example.com / demo1234")
        self.stdout.write("  manager: demo.manager@example.com / demo1234")
