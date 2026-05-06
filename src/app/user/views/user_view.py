from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser

from app.user.models.user_model import CustomUser
from app.user.serializers.user_serializer import (
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
)
from app.user.services.user_service import UserService


class UserViewSet(ModelViewSet):
    """
    使用者 CRUD ViewSet。

    GET    /users/       → list
    POST   /users/       → create
    GET    /users/<id>/  → retrieve
    PUT    /users/<id>/  → update
    DELETE /users/<id>/  → destroy（繼承 ModelViewSet 預設行為）

    只有 Admin 才能存取。
    """

    queryset = CustomUser.objects.all().order_by("date_joined")
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        if self.action in ("update", "partial_update"):
            return UserUpdateSerializer
        return UserSerializer
