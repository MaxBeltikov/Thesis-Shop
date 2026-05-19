from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ActionLogViewSet,
    LoginView,
    MeView,
    RefreshView,
    RegisterView,
)

router = DefaultRouter()
router.register("action-logs", ActionLogViewSet, basename="action-log")

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/refresh/", RefreshView.as_view(), name="auth-refresh"),
    path("auth/me/", MeView.as_view(), name="auth-me"),
    path("", include(router.urls)),
]
