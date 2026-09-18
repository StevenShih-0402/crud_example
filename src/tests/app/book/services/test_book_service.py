"""app.book.services.book_service.BookService 的單元測試。

Service 層是純業務邏輯，測試對象只有它自己：
ORM（Book.objects / instance.save）與 timezone.now 這些外部相依全部 mock 掉，
測試不進資料庫，也不受系統時間影響。
"""

from datetime import date, datetime, timezone as dt_timezone
from unittest.mock import patch

import pytest
from rest_framework import status

from app.book.models.book_model import Book
from app.book.services.book_service import BookService
from core.exception.exceptions import DuplicateResourceError, ResourceNotFoundError

FAKE_NOW = datetime(2026, 9, 9, 12, 0, 0, tzinfo=dt_timezone.utc)


# -----------------------------------------------------------------------------
# validate_book_name_unique
# -----------------------------------------------------------------------------

@patch.object(Book.objects, "filter")
def test_validate_book_name_unique_passes_when_name_is_free(mock_filter):
    """正向：書名沒被用過就安靜通過，不拋任何例外。"""
    # Arrange
    mock_filter.return_value.exists.return_value = False

    # Act
    BookService.validate_book_name_unique("全新的書名")

    # Assert
    mock_filter.assert_called_once_with(book_name="全新的書名")
    mock_filter.return_value.exists.assert_called_once_with()


@patch.object(Book.objects, "filter")
def test_validate_book_name_unique_raises_when_name_is_taken(mock_filter):
    """負向：書名已存在時拋出 DuplicateResourceError（對應 409）。"""
    # Arrange
    mock_filter.return_value.exists.return_value = True

    # Act
    with pytest.raises(DuplicateResourceError) as exc_info:
        BookService.validate_book_name_unique("已存在的書名")

    # Assert
    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert "已存在的書名" in str(exc_info.value.detail)


@patch.object(Book.objects, "filter")
def test_validate_book_name_unique_excludes_self_when_updating(mock_filter):
    """正向：更新情境帶 exclude_id，需先把自己排除再判斷重複。"""
    # Arrange
    mock_filter.return_value.exclude.return_value.exists.return_value = False

    # Act
    BookService.validate_book_name_unique("原本的書名", exclude_id=7)

    # Assert
    mock_filter.assert_called_once_with(book_name="原本的書名")
    mock_filter.return_value.exclude.assert_called_once_with(id=7)


# -----------------------------------------------------------------------------
# get_book
# -----------------------------------------------------------------------------

@patch.object(Book.objects, "get")
def test_get_book_returns_the_book(mock_get):
    """正向：查得到就原樣回傳該 Book。"""
    # Arrange
    expected_book = Book(id=1, book_name="深入淺出 Django")
    mock_get.return_value = expected_book

    # Act
    result = BookService.get_book(1)

    # Assert
    assert result is expected_book
    mock_get.assert_called_once_with(id=1)


@patch.object(Book.objects, "get")
def test_get_book_raises_resource_not_found_when_missing(mock_get):
    """負向：Book.DoesNotExist 要被轉譯成 ResourceNotFoundError（對應 404）。"""
    # Arrange
    mock_get.side_effect = Book.DoesNotExist

    # Act
    with pytest.raises(ResourceNotFoundError) as exc_info:
        BookService.get_book(999)

    # Assert
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "999" in str(exc_info.value.detail)


# -----------------------------------------------------------------------------
# create_book
# -----------------------------------------------------------------------------

@patch("app.book.services.book_service.timezone.now", return_value=FAKE_NOW)
@patch.object(Book.objects, "create")
def test_create_book_fills_created_at(mock_create, mock_now):
    """正向：建立時自動補上 created_at，其餘欄位原樣往下傳。"""
    # Arrange
    validated_data = {
        "book_name": "深入淺出 Django",
        "description": "給後端新手的 Django 入門教學。",
        "writer": "王小明",
        "publish_date": date(2026, 1, 1),
    }

    # Act
    result = BookService.create_book(validated_data)

    # Assert
    assert result is mock_create.return_value
    mock_create.assert_called_once_with(
        book_name="深入淺出 Django",
        description="給後端新手的 Django 入門教學。",
        writer="王小明",
        publish_date=date(2026, 1, 1),
        created_at=FAKE_NOW,
    )


# -----------------------------------------------------------------------------
# update_book
# -----------------------------------------------------------------------------

@patch("app.book.services.book_service.timezone.now", return_value=FAKE_NOW)
@patch.object(Book, "save")
def test_update_book_applies_fields_and_fills_updated_at(mock_save, mock_now):
    """正向：只覆寫有傳入的欄位，並自動補上 updated_at 後存檔。"""
    # Arrange
    instance = Book(
        id=1,
        book_name="舊書名",
        description="舊描述",
        writer="王小明",
        publish_date=date(2020, 1, 1),
    )

    # Act
    result = BookService.update_book(instance, {"book_name": "新書名"})

    # Assert
    assert result is instance
    assert instance.book_name == "新書名"
    assert instance.description == "舊描述"  # 沒傳入的欄位不動
    assert instance.updated_at == FAKE_NOW
    mock_save.assert_called_once_with()
