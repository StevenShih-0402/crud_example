from app.user.models.user_model import CustomUser
from core.exception.exceptions import DuplicateResourceError, ResourceNotFoundError


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
            raise DuplicateResourceError(f"使用者名稱「{username}」已被使用。")

    @staticmethod
    def get_user(user_id) -> CustomUser:
        """依主鍵取得使用者。

        攔截 Django 封裝的 CustomUser.DoesNotExist（繼承自
        django.core.exceptions.ObjectDoesNotExist），轉拋 ResourceNotFoundError，
        最終由 Global Exception Handler 統一處理成 404。
        """
        try:
            return CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            raise ResourceNotFoundError(f"查無 id={user_id} 的使用者。")

    @staticmethod
    def create_user(validated_data: dict) -> CustomUser:
        """建立使用者，使用 set_password() 確保密碼正確雜湊。"""
        password = validated_data.pop("password")
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
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
        return instance
