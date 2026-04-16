from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status

from app.book.serializers.book_serializer import (
    BookSerializer,
    BookCreateSerializer,
    BookUpdateSerializer,
)
from app.book.services.book_service import BookService


class BookViewSet(ModelViewSet):

    def get_queryset(self):
        return BookService.get_all_books()

    def get_object(self):
        return BookService.get_book_by_id(self.kwargs["pk"])

    def get_serializer_class(self):
        if self.action == "create":
            return BookCreateSerializer
        if self.action in ("update", "partial_update"):
            return BookUpdateSerializer
        return BookSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        book = serializer.save()
        return Response(BookSerializer(book).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        book = self.get_object()
        serializer = self.get_serializer(book, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        updated_book = serializer.save()
        return Response(BookSerializer(updated_book).data, status=status.HTTP_200_OK)
