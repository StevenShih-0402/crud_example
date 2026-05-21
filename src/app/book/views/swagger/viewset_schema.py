from drf_spectacular.utils import extend_schema

from app.book.serializers.book_serializer import (
    BookCreateSerializer,
    BookSerializer,
    BookUpdateSerializer,
)
from core.enum.swagger_enum import SwaggerEnum


BOOK_VIEWSET_SCHEMAS = {
    "list": extend_schema(
        summary=SwaggerEnum.BOOK_LIST_SUMMARY.value,
        description=SwaggerEnum.BOOK_LIST_DESCRIPTION.value,
        responses={200: BookSerializer(many=True)},
    ),
    "create": extend_schema(
        summary=SwaggerEnum.BOOK_CREATE_SUMMARY.value,
        description=SwaggerEnum.BOOK_CREATE_DESCRIPTION.value,
        request=BookCreateSerializer,
        responses={201: BookSerializer},
    ),
    "retrieve": extend_schema(
        summary=SwaggerEnum.BOOK_RETRIEVE_SUMMARY.value,
        description=SwaggerEnum.BOOK_RETRIEVE_DESCRIPTION.value,
        responses={200: BookSerializer},
    ),
    "update": extend_schema(
        summary=SwaggerEnum.BOOK_UPDATE_SUMMARY.value,
        description=SwaggerEnum.BOOK_UPDATE_DESCRIPTION.value,
        request=BookUpdateSerializer,
        responses={200: BookSerializer},
    ),
    "partial_update": extend_schema(
        summary=SwaggerEnum.BOOK_PARTIAL_UPDATE_SUMMARY.value,
        description=SwaggerEnum.BOOK_PARTIAL_UPDATE_DESCRIPTION.value,
        request=BookUpdateSerializer,
        responses={200: BookSerializer},
    ),
    "destroy": extend_schema(
        summary=SwaggerEnum.BOOK_DESTROY_SUMMARY.value,
        description=SwaggerEnum.BOOK_DESTROY_DESCRIPTION.value,
        responses={204: None},
    ),
}
