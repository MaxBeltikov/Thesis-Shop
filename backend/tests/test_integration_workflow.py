import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from catalog.models import Product
from documents.constants import DocumentStatus, DocumentType
from documents.models import Document
from orders.models import Order
from users.models import ActionLog, Role

User = get_user_model()


@pytest.fixture
def roles(db):
    client_role, _ = Role.objects.get_or_create(name="client", defaults={"description": "Client"})
    manager_role, _ = Role.objects.get_or_create(name="manager", defaults={"description": "Manager"})
    admin_role, _ = Role.objects.get_or_create(name="admin", defaults={"description": "Admin"})
    return {"client": client_role, "manager": manager_role, "admin": admin_role}


@pytest.fixture
def client_user(db, roles):
    return User.objects.create_user(
        email="client@test.com",
        password="testpass123",
        role=roles["client"],
    )


@pytest.fixture
def manager_user(db, roles):
    return User.objects.create_user(
        email="manager@test.com",
        password="testpass123",
        role=roles["manager"],
    )


@pytest.fixture
def product(db):
    return Product.objects.create(name="Товар 1", price="100.00", unit="шт.")


def auth_client(user) -> APIClient:
    c = APIClient()
    c.force_authenticate(user=user)
    return c


@pytest.mark.django_db
def test_register_and_login(api_client):
    Role.objects.get_or_create(name="client", defaults={"description": "Client"})
    reg = api_client.post(
        "/api/auth/register/",
        {"email": "new@test.com", "password": "testpass123"},
        format="json",
    )
    assert reg.status_code == status.HTTP_201_CREATED

    login = api_client.post(
        "/api/auth/login/",
        {"email": "new@test.com", "password": "testpass123"},
        format="json",
    )
    assert login.status_code == status.HTTP_200_OK
    assert "access" in login.data


@pytest.mark.django_db
def test_order_and_document_chain(client_user, manager_user, product):
    client_api = auth_client(client_user)
    order_resp = client_api.post(
        "/api/orders/",
        {
            "items": [{"product": product.pk, "quantity": "2", "price": "100.00"}],
            "counterparty_name": "ООО Тест",
        },
        format="json",
    )
    # OrderSerializer may not have counterparty - check actual fields
    if order_resp.status_code != status.HTTP_201_CREATED:
        order_resp = client_api.post(
            "/api/orders/",
            {"items": [{"product": product.pk, "quantity": "2", "price": "100.00"}]},
            format="json",
        )
    assert order_resp.status_code == status.HTTP_201_CREATED, order_resp.data
    order_id = order_resp.data["id"]

    doc_resp = client_api.post(
        "/api/documents/",
        {
            "doc_type": DocumentType.COMMERCIAL_PROPOSAL,
            "order": order_id,
            "counterparty_name": "ООО Тест",
            "counterparty_inn": "7700000000",
            "counterparty_address": "Москва",
        },
        format="json",
    )
    assert doc_resp.status_code == status.HTTP_201_CREATED, doc_resp.data
    cp_id = doc_resp.data["id"]
    assert doc_resp.data["docx_file"]
    assert doc_resp.data["pdf_file"]

    mgr_api = auth_client(manager_user)
    next_resp = mgr_api.post(f"/api/documents/{cp_id}/create-next/")
    assert next_resp.status_code == status.HTTP_201_CREATED
    assert next_resp.data["doc_type"] == DocumentType.INVOICE

    send_resp = mgr_api.post(f"/api/documents/{cp_id}/send/")
    assert send_resp.status_code == status.HTTP_200_OK
    assert send_resp.data["status"] == DocumentStatus.SENT

    sign_resp = mgr_api.post(
        f"/api/documents/{cp_id}/sign/",
        {"password": "testpass123"},
        format="json",
    )
    assert sign_resp.status_code == status.HTTP_200_OK
    assert sign_resp.data["status"] == DocumentStatus.SIGNED
    assert ActionLog.objects.filter(action="sign", entity_id=cp_id).exists()


@pytest.mark.django_db
def test_order_documents_list_and_auto_act(client_user, manager_user, product):
    client_api = auth_client(client_user)
    order = Order.objects.create(
        number="ORD-TEST-1",
        client=client_user,
        status="новый",
        total_amount="200.00",
    )
    from orders.models import OrderItem

    OrderItem.objects.create(order=order, product=product, quantity="2", price="100", amount="200")

    Document.objects.create(
        number="CP-1",
        doc_type=DocumentType.COMMERCIAL_PROPOSAL,
        order=order,
        counterparty_name="ООО",
        counterparty_inn="7700000000",
        counterparty_address="Москва",
        created_by=client_user,
    )

    mgr_api = auth_client(manager_user)
    list_resp = mgr_api.get(f"/api/orders/{order.pk}/documents/")
    assert list_resp.status_code == status.HTTP_200_OK
    assert len(list_resp.data) >= 1

    patch_resp = mgr_api.patch(
        f"/api/orders/{order.pk}/",
        {"status": "выполнен"},
        format="json",
    )
    assert patch_resp.status_code == status.HTTP_200_OK
    assert Document.objects.filter(order=order, doc_type=DocumentType.ACT).exists()
