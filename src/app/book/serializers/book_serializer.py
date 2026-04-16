from django.utils import timezone
from rest_framework.serializers import ModelSerializer

from app.book.models.book_model import Book
from app.book.services.book_service import BookService

class BookSerializer(ModelSerializer):

    class Meta:
        model = Book
        fields = "__all__"


class BookCreateSerializer(ModelSerializer):

    class Meta:
        model = Book
        fields = ("book_name", "description", "writer", "publish_date")

    def validate(self, attrs):
        BookService.validate_book_name_unique(attrs["book_name"])
        return attrs

    def create(self, validated_data):
        validated_data["created_at"] = timezone.now()
        return Book.objects.create(**validated_data)


class BookUpdateSerializer(ModelSerializer):

    class Meta:
        model = Book
        fields = ("book_name", "description", "writer", "publish_date")

    def validate(self, attrs):
        BookService.validate_book_name_unique(
            attrs["book_name"],
            exclude_id=self.instance.id,
        )
        return attrs

    def update(self, instance, validated_data):
        validated_data["updated_at"] = timezone.now()
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance
