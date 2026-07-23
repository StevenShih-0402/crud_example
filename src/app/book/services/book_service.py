import logging

from django.utils import timezone

from app.book.models.book_model import Book
from core.exception.exceptions import DuplicateResourceError, ResourceNotFoundError

# Django 標準做法：以模組路徑（__name__，此處為 app.book.services.book_service）
# 命名 logger。settings.LOGGING 裡設定的 "app" logger 會依 logging 的階層繼承
# 自動套用到這裡，不需要在設定檔逐一列出每個模組。
logger = logging.getLogger(__name__)


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
            # WARNING：使用者輸入造成的可預期失敗，不是系統故障，故不用 ERROR。
            # 參數用 %s 佔位符交給 logging 格式化（而非 f-string），
            # 這樣訊息被過濾掉時就不會白白付出字串拼接成本。
            logger.warning("書名重複，拒絕寫入：book_name=%s, exclude_id=%s", book_name, exclude_id)
            raise DuplicateResourceError(f"書名「{book_name}」已存在，請使用其他名稱。")

    # -------------------------------------------------------------------------
    # 查詢
    # -------------------------------------------------------------------------

    @staticmethod
    def get_book(book_id) -> Book:
        """依主鍵取得書本。

        以 Book.objects.get() 查詢，攔截 Django 封裝的 Book.DoesNotExist
        （繼承自 django.core.exceptions.ObjectDoesNotExist），轉拋業務語意的
        ResourceNotFoundError，最終由 Global Exception Handler 統一處理成 404。
        """
        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            logger.warning("查無書本：book_id=%s", book_id)
            raise ResourceNotFoundError(f"查無 id={book_id} 的書本。")

        # DEBUG：只落檔、不上 console，需要細追查詢軌跡時才派上用場
        logger.debug("取得書本：book_id=%s, book_name=%s", book.id, book.book_name)
        return book

    # -------------------------------------------------------------------------
    # CRUD 操作（供 Serializer.create() / update() 呼叫）
    # -------------------------------------------------------------------------

    @staticmethod
    def create_book(validated_data: dict) -> Book:
        """建立書本並自動寫入 created_at。"""
        validated_data["created_at"] = timezone.now()
        book = Book.objects.create(**validated_data)
        logger.info("建立書本成功：book_id=%s, book_name=%s", book.id, book.book_name)
        return book

    @staticmethod
    def update_book(instance: Book, validated_data: dict) -> Book:
        """更新書本並自動寫入 updated_at。"""
        validated_data["updated_at"] = timezone.now()
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        # 記錄異動了哪些欄位，日後可回推資料為何變成現在的樣子
        logger.info(
            "更新書本成功：book_id=%s, fields=%s",
            instance.id,
            sorted(validated_data.keys()),
        )
        return instance
