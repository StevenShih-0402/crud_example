from rest_framework.serializers import ModelSerializer

from app.book.models.book_model import Book
from app.book.services.book_service import BookService


class BookSerializer(ModelSerializer):

    class Meta:
        model = Book
        fields = [
            "id",
            "book_name",
            "description",
            "writer",
            "publish_date",
            "created_at",
            "updated_at",
        ]


class BookCreateSerializer(ModelSerializer):

    class Meta:
        model = Book
        fields = [
            "book_name",
            "description",
            "writer",
            "publish_date",
        ]


class BookUpdateSerializer(ModelSerializer):

    class Meta:
        model = Book
        fields = [
            "book_name",
            "description",
            "writer",
            "publish_date",
        ]
