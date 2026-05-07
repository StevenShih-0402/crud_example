from django.utils import timezone
from rest_framework.exceptions import ValidationError

from app.book.models.book_model import Book


class BookService:
    """
    書本業務邏輯層（Service Layer）。

    負責處理與書本相關的商業規則，讓 Serializer 和 View 保持乾淨。
    """

    # -------------------------------------------------------------------------
    # 驗證（供 Serializer.validate() 呼叫）
    # -------------------------------------------------------------------------

    @staticmethod
    def validate_book_name_unique(book_name: str, exclude_id: int | None = None):
        """
        驗證書名不得重複。

        - 新增時：exclude_id=None，只要名稱存在就報錯。
        - 更新時：exclude_id=instance.id，排除自身後再檢查。
        """
        qs = Book.objects.filter(book_name=book_name)
        if exclude_id is not None:
            qs = qs.exclude(id=exclude_id)
        if qs.exists():
            raise ValidationError({"book_name": f"書名「{book_name}」已存在，請使用其他名稱。"})

    # -------------------------------------------------------------------------
    # CRUD 操作（供 Serializer.create() / update() 呼叫）
    # -------------------------------------------------------------------------

    @staticmethod
    def create_book(validated_data: dict) -> Book:
        """建立書本並自動寫入 created_at。"""
        validated_data["created_at"] = timezone.now()
        return Book.objects.create(**validated_data)

    @staticmethod
    def update_book(instance: Book, validated_data: dict) -> Book:
        """更新書本並自動寫入 updated_at。"""
        validated_data["updated_at"] = timezone.now()
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance
