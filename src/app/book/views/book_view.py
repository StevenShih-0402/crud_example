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
