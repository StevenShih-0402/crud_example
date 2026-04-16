from rest_framework.exceptions import ValidationError

from app.book.models.book_model import Book


class BookService:

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

    @staticmethod
    def get_all_books():
        """取得所有書本，依建立時間由新到舊排序。"""
        return Book.objects.all().order_by("-created_at")

    @staticmethod
    def get_book_by_id(book_id: int) -> Book:
        """依 ID 取得單本書，找不到時拋出 ValidationError (400)"""
        try:
            return Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            raise ValidationError({"id": f"書本 ID={book_id} 不存在。"})
