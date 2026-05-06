from rest_framework.serializers import ModelSerializer, CharField

from app.user.models.user_model import CustomUser
from app.user.services.user_service import UserService


class UserSerializer(ModelSerializer):
    """通用唯讀序列化器，用於回傳使用者資料。"""

    class Meta:
        model = CustomUser
        fields = ["id", "username", "email", "phone", "is_active", "date_joined"]


class UserCreateSerializer(ModelSerializer):
    """
    新增使用者專用序列化器。

    職責：
      1. validate()  — 驗證 username 唯一性。
      2. create()    — 呼叫 Service 層，確保密碼雜湊後存入 DB。
    """

    # write_only=True：password 只用於輸入，不會出現在回傳資料中。
    password = CharField(write_only=True, min_length=8)

    class Meta:
        model = CustomUser
        fields = ["username", "email", "password", "phone"]

    def validate(self, attrs):
        UserService.validate_username_unique(attrs["username"])
        return attrs

    def create(self, validated_data):
        return UserService.create_user(validated_data)


class UserUpdateSerializer(ModelSerializer):
    """
    更新使用者專用序列化器。

    password 為選填；若傳入則由 Service 層重新雜湊。
    """

    password = CharField(write_only=True, min_length=8, required=False)

    class Meta:
        model = CustomUser
        fields = ["username", "email", "password", "phone"]

    def validate(self, attrs):
        if "username" in attrs:
            UserService.validate_username_unique(
                attrs["username"],
                exclude_id=self.instance.id,
            )
        return attrs

    def update(self, instance, validated_data):
        return UserService.update_user(instance, validated_data)
