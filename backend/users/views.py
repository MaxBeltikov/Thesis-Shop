from rest_framework import generics, permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .audit import log_action
from .models import ActionLog
from .permissions import IsManagerOrAdmin
from .serializers import ActionLogSerializer, RegisterSerializer, UserSerializer


class RegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        log_action(user, "register", "user", user.pk, self.request)


class LoginView(TokenObtainPairView):
    """JWT: выдача access/refresh по email и паролю."""

    permission_classes = [permissions.AllowAny]


class RefreshView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class ActionLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Журнал действий: только менеджер и администратор."""

    serializer_class = ActionLogSerializer
    permission_classes = [IsManagerOrAdmin]

    def get_queryset(self):
        return ActionLog.objects.select_related("user").order_by("-created_at")
