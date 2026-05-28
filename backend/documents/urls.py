from rest_framework.routers import DefaultRouter

from .views import DocumentTemplateViewSet, DocumentViewSet

router = DefaultRouter()
router.register("templates", DocumentTemplateViewSet, basename="document-template")
router.register("documents", DocumentViewSet, basename="document")

urlpatterns = router.urls
