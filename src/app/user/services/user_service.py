import logging

from app.user.models.user_model import CustomUser
from core.exception.exceptions import DuplicateResourceError, ResourceNotFoundError

# Django 標準做法：logger 以模組路徑（__name__）命名，
# 由 settings.LOGGING 的 "app" logger 依階層繼承套用設定。
logger = logging.getLogger(__name__)


class UserService:
    """
    使用者業務邏輯層（Service Layer）。
    """

    @staticmethod
    def validate_username_unique(username: str, exclude_id: int | None = None):
        qs = CustomUser.objects.filter(username=username)
        if exclude_id is not None:
            qs = qs.exclude(id=exclude_id)
        if qs.exists():
            logger.warning("使用者名稱重複，拒絕寫入：username=%s, exclude_id=%s", username, exclude_id)
            raise DuplicateResourceError(f"使用者名稱「{username}」已被使用。")

    @staticmethod
    def get_user(user_id) -> CustomUser:
        """依主鍵取得使用者。

        攔截 Django 封裝的 CustomUser.DoesNotExist（繼承自
        django.core.exceptions.ObjectDoesNotExist），轉拋 ResourceNotFoundError，
        最終由 Global Exception Handler 統一處理成 404。
        """
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            logger.warning("查無使用者：user_id=%s", user_id)
            raise ResourceNotFoundError(f"查無 id={user_id} 的使用者。")

        logger.debug("取得使用者：user_id=%s, username=%s", user.id, user.username)
        return user

    @staticmethod
    def create_user(validated_data: dict) -> CustomUser:
        """建立使用者，使用 set_password() 確保密碼正確雜湊。"""
        password = validated_data.pop("password")
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        # 注意：log 只記錄 id / username 等識別資訊。
        # password、token 這類機密絕不可寫進 log——log 會落檔且常被集中收集。
        logger.info("建立使用者成功：user_id=%s, username=%s", user.id, user.username)
        return user

    @staticmethod
    def update_user(instance: CustomUser, validated_data: dict) -> CustomUser:
        """更新使用者，若有傳入 password 則重新雜湊。"""
        password = validated_data.pop("password", None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        if password:
            instance.set_password(password)
        instance.save()
        # 只記錄「有沒有改密碼」這個事實，不記錄密碼內容
        logger.info(
            "更新使用者成功：user_id=%s, fields=%s, password_changed=%s",
            instance.id,
            sorted(validated_data.keys()),
            bool(password),
        )
        return instance
