import logging

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

logger = logging.getLogger(__name__)


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

    # -------------------------------------------------------------------------
    # 寫入類操作的 log
    #
    # 帳號異動屬敏感操作，一律記錄「哪個管理員動了哪個帳號」，
    # 以 DRF 的 perform_* 掛載點實作，不改動原本的 HTTP 流程。
    # -------------------------------------------------------------------------

    def perform_create(self, serializer):
        super().perform_create(serializer)
        logger.info("管理員 %s 新增使用者 user_id=%s", self.request.user, serializer.instance.id)

    def perform_update(self, serializer):
        super().perform_update(serializer)
        logger.info("管理員 %s 更新使用者 user_id=%s", self.request.user, serializer.instance.id)

    def perform_destroy(self, instance):
        # 刪除後物件即消失，先把識別資訊留下來再刪
        user_id, username = instance.id, instance.username
        super().perform_destroy(instance)
        logger.info(
            "管理員 %s 刪除使用者 user_id=%s, username=%s",
            self.request.user,
            user_id,
            username,
        )
