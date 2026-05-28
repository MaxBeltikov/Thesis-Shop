import secrets
from decimal import Decimal

from django.utils import timezone
from rest_framework import serializers

from documents.services.workflow import ORDER_COMPLETED_STATUSES, auto_create_act_for_order
from users.audit import log_action
from users.permissions import is_manager_or_admin

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_name", "quantity", "price", "amount"]
        read_only_fields = ["id", "amount", "product_name"]

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Количество должно быть больше нуля.")
        return value

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Цена не может быть отрицательной.")
        return value


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, required=False)
    client_email = serializers.EmailField(source="client.email", read_only=True)
    manager_email = serializers.EmailField(source="manager.email", read_only=True, allow_null=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "number",
            "client",
            "client_email",
            "manager",
            "manager_email",
            "status",
            "total_amount",
            "items",
            "created_at",
            "updated_at",
            "completed_at",
        ]
        read_only_fields = ["id", "total_amount", "created_at", "updated_at", "client_email", "manager_email"]
        extra_kwargs = {
            "number": {"required": False, "allow_blank": True},
            "client": {"required": False},
            "manager": {"required": False},
        }

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Заказ должен содержать хотя бы одну позицию.")
        return value

    def validate_client(self, value):
        request = self.context.get("request")
        user = request.user if request else None
        if value and user and not is_manager_or_admin(user) and value != user:
            raise serializers.ValidationError("Нельзя оформить заказ на другого клиента.")
        return value

    def validate(self, attrs):
        request = self.context.get("request")
        user = request.user if request else None
        if self.instance is None:
            if attrs.get("client") is None:
                if is_manager_or_admin(user):
                    raise serializers.ValidationError({"client": "Укажите клиента для заказа."})
                attrs["client"] = user
            if not attrs.get("items"):
                raise serializers.ValidationError({"items": "Заказ должен содержать хотя бы одну позицию."})
        return attrs

    def _sync_items(self, order: Order, items_data: list[dict]) -> Decimal:
        order.items.all().delete()
        total = Decimal("0")
        for row in items_data:
            product = row["product"]
            quantity = row["quantity"]
            price = row["price"]
            amount = (quantity * price).quantize(Decimal("0.01"))
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=price,
                amount=amount,
            )
            total += amount
        return total

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        if not validated_data.get("number"):
            validated_data["number"] = f"ORD-{timezone.now().strftime('%Y%m%d')}-{secrets.token_hex(4).upper()}"
        order = Order.objects.create(**validated_data)
        total = self._sync_items(order, items_data)
        order.total_amount = total
        order.save(update_fields=["total_amount"])
        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop("items", None)
        old_status = instance.status
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if items_data is not None:
            total = self._sync_items(instance, items_data)
            instance.total_amount = total
            instance.save(update_fields=["total_amount"])

        new_status = (instance.status or "").lower()
        if (
            old_status.lower() not in ORDER_COMPLETED_STATUSES
            and new_status in ORDER_COMPLETED_STATUSES
        ):
            if not instance.completed_at:
                instance.completed_at = timezone.now()
                instance.save(update_fields=["completed_at"])
            request = self.context.get("request")
            user = request.user if request else instance.client
            act = auto_create_act_for_order(instance, user)
            if act and request:
                log_action(
                    user,
                    "auto_create_act",
                    "document",
                    act.pk,
                    request,
                    details={"order_id": instance.pk},
                )
        return instance
