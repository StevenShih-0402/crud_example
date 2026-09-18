"""app.user.services.user_service.UserService 的單元測試。

與 BookService 相同的策略：ORM（CustomUser.objects / instance.save）與
密碼雜湊（set_password）都 mock 掉，只驗證 Service 自己的業務邏輯。
"""

from unittest.mock import patch

import pytest
from rest_framework import status

from app.user.models.user_model import CustomUser
from app.user.services.user_service import UserService
from core.exception.exceptions import DuplicateResourceError, ResourceNotFoundError


# -----------------------------------------------------------------------------
# validate_username_unique
# -----------------------------------------------------------------------------

@patch.object(CustomUser.objects, "filter")
def test_validate_username_unique_passes_when_username_is_free(mock_filter):
    """正向：帳號沒被用過就安靜通過，不拋任何例外。"""
    # Arrange
    mock_filter.return_value.exists.return_value = False

    # Act
    UserService.validate_username_unique("new_user")

    # Assert
    mock_filter.assert_called_once_with(username="new_user")
    mock_filter.return_value.exists.assert_called_once_with()


@patch.object(CustomUser.objects, "filter")
def test_validate_username_unique_raises_when_username_is_taken(mock_filter):
    """負向：帳號已被使用時拋出 DuplicateResourceError（對應 409）。"""
    # Arrange
    mock_filter.return_value.exists.return_value = True

    # Act
    with pytest.raises(DuplicateResourceError) as exc_info:
        UserService.validate_username_unique("existing_user")

    # Assert
    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert "existing_user" in str(exc_info.value.detail)


@patch.object(CustomUser.objects, "filter")
def test_validate_username_unique_excludes_self_when_updating(mock_filter):
    """正向：更新情境帶 exclude_id，需先把自己排除再判斷重複。"""
    # Arrange
    mock_filter.return_value.exclude.return_value.exists.return_value = False

    # Act
    UserService.validate_username_unique("existing_user", exclude_id=7)

    # Assert
    mock_filter.assert_called_once_with(username="existing_user")
    mock_filter.return_value.exclude.assert_called_once_with(id=7)


# -----------------------------------------------------------------------------
# get_user
# -----------------------------------------------------------------------------

@patch.object(CustomUser.objects, "get")
def test_get_user_returns_the_user(mock_get):
    """正向：查得到就原樣回傳該 CustomUser。"""
    # Arrange
    expected_user = CustomUser(id=1, username="new_user")
    mock_get.return_value = expected_user

    # Act
    result = UserService.get_user(1)

    # Assert
    assert result is expected_user
    mock_get.assert_called_once_with(id=1)


@patch.object(CustomUser.objects, "get")
def test_get_user_raises_resource_not_found_when_missing(mock_get):
    """負向：CustomUser.DoesNotExist 要被轉譯成 ResourceNotFoundError（對應 404）。"""
    # Arrange
    mock_get.side_effect = CustomUser.DoesNotExist

    # Act
    with pytest.raises(ResourceNotFoundError) as exc_info:
        UserService.get_user(999)

    # Assert
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "999" in str(exc_info.value.detail)


# -----------------------------------------------------------------------------
# create_user
# -----------------------------------------------------------------------------

@patch.object(CustomUser, "save")
@patch.object(CustomUser, "set_password")
def test_create_user_hashes_password_and_saves(mock_set_password, mock_save):
    """正向：password 不可直接塞進欄位，必須交給 set_password 雜湊後才存檔。"""
    # Arrange
    validated_data = {
        "username": "new_user",
        "email": "new_user@example.com",
        "phone": "0912345678",
        "password": "sup3r-secret",
    }

    # Act
    result = UserService.create_user(validated_data)

    # Assert
    assert result.username == "new_user"
    assert result.email == "new_user@example.com"
    assert result.phone == "0912345678"
    mock_set_password.assert_called_once_with("sup3r-secret")
    mock_save.assert_called_once_with()


# -----------------------------------------------------------------------------
# update_user
# -----------------------------------------------------------------------------

@patch.object(CustomUser, "save")
@patch.object(CustomUser, "set_password")
def test_update_user_rehashes_password_when_provided(mock_set_password, mock_save):
    """正向：有帶 password 時要重新雜湊，其餘欄位照常覆寫。"""
    # Arrange
    instance = CustomUser(id=1, username="old_user", email="old@example.com")

    # Act
    result = UserService.update_user(
        instance, {"username": "new_user", "password": "new-sup3r-secret"}
    )

    # Assert
    assert result is instance
    assert instance.username == "new_user"
    assert instance.email == "old@example.com"  # 沒傳入的欄位不動
    mock_set_password.assert_called_once_with("new-sup3r-secret")
    mock_save.assert_called_once_with()


@patch.object(CustomUser, "save")
@patch.object(CustomUser, "set_password")
def test_update_user_keeps_password_when_not_provided(mock_set_password, mock_save):
    """負向：沒帶 password 時絕不能誤呼叫 set_password，否則會把密碼洗掉。"""
    # Arrange
    instance = CustomUser(id=1, username="old_user", email="old@example.com")

    # Act
    UserService.update_user(instance, {"email": "new@example.com"})

    # Assert
    assert instance.email == "new@example.com"
    mock_set_password.assert_not_called()
    mock_save.assert_called_once_with()
