from rest_framework.serializers import ModelSerializer

from app.book.models.book_model import Book
from app.book.services.book_service import BookService


class BookSerializer(ModelSerializer):
    """
    唯讀序列化器，用於回傳書本資料（list / retrieve）。
    """

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
    """
    新增書本專用序列化器。

    職責：
      1. validate()  — 呼叫 Service 層執行業務邏輯驗證（書名唯一性）。
      2. create()    — 呼叫 Service 層建立資料，並自動寫入 created_at。
    """

    class Meta:
        model = Book
        fields = [
            "book_name",
            "description",
            "writer",
            "publish_date",
        ]

    def validate(self, attrs):
        BookService.validate_book_name_unique(attrs["book_name"])
        return attrs

    def create(self, validated_data):
        return BookService.create_book(validated_data)


class BookUpdateSerializer(ModelSerializer):
    """
    更新書本專用序列化器。

    職責：
      1. validate()  — 呼叫 Service 層執行業務邏輯驗證（書名唯一性，排除自身）。
      2. update()    — 呼叫 Service 層更新資料，並自動寫入 updated_at。
    """

    class Meta:
        model = Book
        fields = [
            "book_name",
            "description",
            "writer",
            "publish_date",
        ]

    def validate(self, attrs):
        BookService.validate_book_name_unique(
            attrs["book_name"],
            exclude_id=self.instance.id,
        )
        return attrs

    def update(self, instance, validated_data):
        return BookService.update_book(instance, validated_data)
