"""app.user.views.user_view 的端點測試。

與 book 端點相同的串接測試，另外多兩件事：
  1. users 端點要求 IsAdminUser，因此使用 admin_client。
  2. CustomUser.username 是 unique 欄位，ModelSerializer 會自動掛上
     DRF 的 UniqueValidator，它會去查資料庫；本測試不碰 DB，
     故連同它實際執行查詢的 rest_framework.validators.qs_exists 一併 mock。
"""

from unittest.mock import patch

from rest_framework import status

from app.user.models.user_model import CustomUser
from core.enum.error_enum import ErrorEnum
from core.exception.exceptions import DuplicateResourceError

USERS_URL = "/users/"

USER_PAYLOAD = {
    "username": "new_user",
    "email": "new_user@example.com",
    "password": "sup3r-secret",  # write_only，不應出現在回應中
    "phone": "0912345678",
}


@patch("rest_framework.validators.qs_exists", return_value=False)
@patch("app.user.services.user_service.UserService.create_user")
@patch("app.user.services.user_service.UserService.validate_username_unique")
def test_create_user_success(
    mock_validate_unique, mock_create_user, mock_qs_exists, admin_client
):
    """正向：POST /users/ 建立成功，回傳統一格式且不外洩 password。"""
    # Arrange：讓 Service 回傳一個「彷彿已存檔」的 CustomUser（僅建物件，不進 DB）
    mock_create_user.return_value = CustomUser(
        id=1,
        username=USER_PAYLOAD["username"],
        email=USER_PAYLOAD["email"],
        phone=USER_PAYLOAD["phone"],
    )

    # Act
    response = admin_client.post(USERS_URL, USER_PAYLOAD, format="json")

    # Assert：middleware 會把成功回應統一成 HTTP 200，原始狀態碼保留在 code
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["code"] == status.HTTP_201_CREATED
    assert body["msg"] == "SUCCESS"
    assert body["data"] == {
        "username": USER_PAYLOAD["username"],
        "email": USER_PAYLOAD["email"],
        "phone": USER_PAYLOAD["phone"],
    }

    # Assert：Service 層確實被呼叫，且密碼有交給它去做雜湊
    mock_validate_unique.assert_called_once_with(USER_PAYLOAD["username"])
    mock_create_user.assert_called_once()
    validated_data = mock_create_user.call_args.args[0]
    assert validated_data["username"] == USER_PAYLOAD["username"]
    assert validated_data["password"] == USER_PAYLOAD["password"]


@patch("rest_framework.validators.qs_exists", return_value=False)
@patch("app.user.services.user_service.UserService.create_user")
@patch("app.user.services.user_service.UserService.validate_username_unique")
def test_create_user_with_duplicate_username_returns_409(
    mock_validate_unique, mock_create_user, mock_qs_exists, admin_client
):
    """負向：帳號重複時 Service 拋 DuplicateResourceError，端點回 409 錯誤格式。"""
    # Arrange
    detail = f"使用者名稱「{USER_PAYLOAD['username']}」已被使用。"
    mock_validate_unique.side_effect = DuplicateResourceError(detail)

    # Act
    response = admin_client.post(USERS_URL, USER_PAYLOAD, format="json")

    # Assert：錯誤維持原 HTTP 狀態碼，內容由 Global Exception Handler 統一組裝
    assert response.status_code == status.HTTP_409_CONFLICT
    body = response.json()
    assert body["code"] == ErrorEnum.DUPLICATE_RESOURCE.name
    assert body["msg"] == ErrorEnum.DUPLICATE_RESOURCE.value
    assert body["data"] == {"detail": detail}

    # Assert：驗證沒過就不該寫入
    mock_create_user.assert_not_called()
