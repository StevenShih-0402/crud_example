from rest_framework.exceptions import ValidationError

from app.user.models.user_model import CustomUser


class UserService:
    """
    使用者業務邏輯層（Service Layer）。
    """

    @staticmethod
    def get_all_users():
        return CustomUser.objects.all().order_by("date_joined")

    @staticmethod
    def get_user_by_id(user_id: int) -> CustomUser:
        try:
            return CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            raise ValidationError({"id": f"使用者 ID={user_id} 不存在。"})

    @staticmethod
    def validate_username_unique(username: str, exclude_id: int | None = None):
        qs = CustomUser.objects.filter(username=username)
        if exclude_id is not None:
            qs = qs.exclude(id=exclude_id)
        if qs.exists():
            raise ValidationError({"username": f"使用者名稱「{username}」已被使用。"})

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
