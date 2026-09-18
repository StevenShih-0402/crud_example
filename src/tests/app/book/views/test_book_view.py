"""app.book.views.book_view 的端點測試。

測試對象是 HTTP 端點本身，涵蓋一整條串接：
    Serializer 驗證 → Service 層 → Global Exception Handler → 回應格式 middleware

BookService 屬於外部相依，一律 mock 掉，測試不觸及資料庫。
"""

import datetime
from unittest.mock import patch

from rest_framework import status

from app.book.models.book_model import Book
from core.enum.error_enum import ErrorEnum
from core.exception.exceptions import DuplicateResourceError

BOOKS_URL = "/books/"

# 送進端點的 request body（publish_date 以字串傳入，由 serializer 轉型）
BOOK_PAYLOAD = {
    "book_name": "深入淺出 Django",
    "description": "給後端新手的 Django 入門教學。",
    "writer": "王小明",
    "publish_date": "2026-01-01",
}


@patch("app.book.services.book_service.BookService.create_book")
@patch("app.book.services.book_service.BookService.validate_book_name_unique")
def test_create_book_success(mock_validate_unique, mock_create_book, authenticated_client):
    """正向：POST /books/ 建立成功，回傳統一格式且 code 為 201。"""
    # Arrange：讓 Service 回傳一個「彷彿已存檔」的 Book（僅建物件，不進 DB）
    mock_create_book.return_value = Book(
        id=1,
        book_name=BOOK_PAYLOAD["book_name"],
        description=BOOK_PAYLOAD["description"],
        writer=BOOK_PAYLOAD["writer"],
        publish_date=datetime.date(2026, 1, 1),
    )

    # Act
    response = authenticated_client.post(BOOKS_URL, BOOK_PAYLOAD, format="json")

    # Assert：middleware 會把成功回應統一成 HTTP 200，原始狀態碼保留在 code
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["code"] == status.HTTP_201_CREATED
    assert body["msg"] == "SUCCESS"
    assert body["data"] == {
        "book_name": BOOK_PAYLOAD["book_name"],
        "description": BOOK_PAYLOAD["description"],
        "writer": BOOK_PAYLOAD["writer"],
        "publish_date": BOOK_PAYLOAD["publish_date"],
    }

    # Assert：Service 層確實被呼叫，且拿到轉型後的 validated_data
    mock_validate_unique.assert_called_once_with(BOOK_PAYLOAD["book_name"])
    mock_create_book.assert_called_once()
    validated_data = mock_create_book.call_args.args[0]
    assert validated_data["book_name"] == BOOK_PAYLOAD["book_name"]
    assert validated_data["publish_date"] == datetime.date(2026, 1, 1)


@patch("app.book.services.book_service.BookService.create_book")
@patch("app.book.services.book_service.BookService.validate_book_name_unique")
def test_create_book_with_duplicate_name_returns_409(
    mock_validate_unique, mock_create_book, authenticated_client
):
    """負向：書名重複時 Service 拋 DuplicateResourceError，端點回 409 錯誤格式。"""
    # Arrange
    detail = f"書名「{BOOK_PAYLOAD['book_name']}」已存在，請使用其他名稱。"
    mock_validate_unique.side_effect = DuplicateResourceError(detail)

    # Act
    response = authenticated_client.post(BOOKS_URL, BOOK_PAYLOAD, format="json")

    # Assert：錯誤維持原 HTTP 狀態碼，內容由 Global Exception Handler 統一組裝
    assert response.status_code == status.HTTP_409_CONFLICT
    body = response.json()
    assert body["code"] == ErrorEnum.DUPLICATE_RESOURCE.name
    assert body["msg"] == ErrorEnum.DUPLICATE_RESOURCE.value
    assert body["data"] == {"detail": detail}

    # Assert：驗證沒過就不該寫入
    mock_create_book.assert_not_called()
