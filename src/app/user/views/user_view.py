from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet

from app.user.models.user_model import CustomUser
from app.user.serializers.user_serializer import (
    UserCreateSerializer,
    UserSerializer,
    UserUpdateSerializer,
)
from app.user.services.user_service import UserService


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

    def get_object(self):
        # 改走 Service 層查詢，查無資料由 UserService.get_user 轉拋
        # ResourceNotFoundError，再由 Global Exception Handler 統一成 404。
        user = UserService.get_user(self.kwargs[self.lookup_field])
        self.check_object_permissions(self.request, user)
        return user
