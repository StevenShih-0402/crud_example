from rest_framework.viewsets import ModelViewSet

from drf_spectacular.utils import extend_schema, extend_schema_view
from app.book.models.book_model import Book
from app.book.serializers.book_serializer import (
    BookSerializer,
    BookCreateSerializer,
    BookUpdateSerializer,
)
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
