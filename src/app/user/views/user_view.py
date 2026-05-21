from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet

from app.user.models.user_model import CustomUser
from app.user.serializers.user_serializer import (
    UserCreateSerializer,
    UserSerializer,
    UserUpdateSerializer,
)


class UserViewSet(ModelViewSet):

    queryset = CustomUser.objects.all().order_by("date_joined")
    permission_classes = [IsAdminUser]
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        if self.action in ("update", "partial_update"):
            return UserUpdateSerializer
        return UserSerializer
