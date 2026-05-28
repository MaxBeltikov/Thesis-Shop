from rest_framework import viewsets

from users.audit import log_action
from users.permissions import IsManagerOrAdminOrReadOnly

from .models import Product
from .serializers import ProductSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by("-created_at")
    serializer_class = ProductSerializer
    permission_classes = [IsManagerOrAdminOrReadOnly]

    def perform_create(self, serializer):
        instance = serializer.save()
        log_action(self.request.user, "create", "product", instance.pk, self.request)

    def perform_update(self, serializer):
        instance = serializer.save()
        log_action(self.request.user, "update", "product", instance.pk, self.request)

    def perform_destroy(self, instance):
        pk = instance.pk
        instance.delete()
        log_action(self.request.user, "delete", "product", pk, self.request)
