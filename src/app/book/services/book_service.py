from django.utils import timezone
from rest_framework.exceptions import ValidationError

from app.book.models.book_model import Book


class BookService:
    """
    書本業務邏輯層（Service Layer）。

    負責處理與書本相關的商業規則，讓 Serializer 和 View 保持乾淨。
    """

    # -------------------------------------------------------------------------
    # 查詢
    # -------------------------------------------------------------------------

    @staticmethod
    def get_all_books():
        """取得所有書本，依建立時間由新到舊排序。"""
        return Book.objects.all().order_by("-created_at")

    @staticmethod
    def get_book_by_id(book_id: int) -> Book:
        """
        依 ID 取得單本書，找不到時拋出 ValidationError
        （在教學範例中統一用 DRF 的 ValidationError 回傳 400；
          實務上可改用 Http404 / get_object_or_404 回傳 404）。
        """
        try:
            return Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            raise ValidationError({"id": f"書本 ID={book_id} 不存在。"})

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
        """
        建立書本並自動寫入 created_at。
        """
        validated_data["created_at"] = timezone.now()
        return Book.objects.create(**validated_data)

    @staticmethod
    def update_book(instance: Book, validated_data: dict) -> Book:
        """
        更新書本並自動寫入 updated_at。
        """
        validated_data["updated_at"] = timezone.now()
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance

    @staticmethod
    def delete_book(instance: Book) -> None:
        """刪除書本。"""
        instance.delete()
