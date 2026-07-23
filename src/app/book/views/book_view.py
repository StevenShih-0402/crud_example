import logging

from rest_framework.viewsets import ModelViewSet

from drf_spectacular.utils import extend_schema, extend_schema_view
from app.book.models.book_model import Book
from app.book.serializers.book_serializer import (
    BookSerializer,
    BookCreateSerializer,
    BookUpdateSerializer,
)
from app.book.services.book_service import BookService
from app.book.views.swagger.viewset_schema import BOOK_VIEWSET_SCHEMAS

logger = logging.getLogger(__name__)

@extend_schema(tags=["書籍 (Book)"])  # Swagger 下拉選單中的標題
@extend_schema_view(**BOOK_VIEWSET_SCHEMAS)
class BookViewSet(ModelViewSet):
    """
    書本 CRUD ViewSet。

    GET    /books/       → list
    POST   /books/       → create
    GET    /books/<pk>/  → retrieve
    PUT    /books/<pk>/  → update
    PATCH  /books/<pk>/  → partial_update
    DELETE /books/<pk>/  → destroy
    """

    queryset = Book.objects.all().order_by("-created_at")

    def get_serializer_class(self):
        if self.action == "create":
            return BookCreateSerializer
        if self.action in ("update", "partial_update"):
            return BookUpdateSerializer
        return BookSerializer

    def get_object(self):
        # 改走 Service 層查詢，查無資料由 BookService.get_book 轉拋
        # ResourceNotFoundError，再由 Global Exception Handler 統一成 404。
        book = BookService.get_book(self.kwargs[self.lookup_field])
        self.check_object_permissions(self.request, book)
        return book

    # -------------------------------------------------------------------------
    # 寫入類操作的 log
    #
    # 覆寫 DRF 提供的 perform_* 掛載點（而非整個 create/update/destroy），
    # 是在 ViewSet 補記錄的標準做法：只加 log、不動 HTTP 流程。
    # View 層記錄「誰做了什麼」，Service 層記錄「資料實際變成什麼」，兩者互補。
    # -------------------------------------------------------------------------

    def perform_create(self, serializer):
        super().perform_create(serializer)
        logger.info("使用者 %s 新增書本 book_id=%s", self.request.user, serializer.instance.id)

    def perform_update(self, serializer):
        super().perform_update(serializer)
        logger.info("使用者 %s 更新書本 book_id=%s", self.request.user, serializer.instance.id)

    def perform_destroy(self, instance):
        # 刪除後物件即消失，先把識別資訊留下來再刪
        book_id, book_name = instance.id, instance.book_name
        super().perform_destroy(instance)
        logger.info(
            "使用者 %s 刪除書本 book_id=%s, book_name=%s",
            self.request.user,
            book_id,
            book_name,
        )
