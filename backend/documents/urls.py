from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import DocumentTemplateViewSet, DocumentViewSet

router = DefaultRouter()
router.register("templates", DocumentTemplateViewSet, basename="document-template")
# Пустой префикс: /api/documents/{id}/, /api/documents/{id}/sign/, /api/documents/{id}/send/
router.register("", DocumentViewSet, basename="document")

urlpatterns = [
    path("", include(router.urls)),
]
