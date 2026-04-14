from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from app.book.serializers.book_serializer import (
    BookSerializer,
    BookCreateSerializer,
    BookUpdateSerializer,
)
from app.book.services.book_service import BookService


class BookView(APIView):

    def _get_book_or_400(self, book_id: int):
        """共用的取書邏輯，找不到時由 Service 層拋出 ValidationError（400）。"""
        return BookService.get_book_by_id(book_id)
        
    def get(self, request: Request) -> Response:
        # ── 1. 呼叫 Service 層取得資料 ──
        books = BookService.get_all_books()

        # ── 2. 將 queryset 序列化（many=True 代表序列化多筆資料） ──
        serializer = BookSerializer(books, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        # ── 1. 將 request.data 丟入 Serializer ──
        serializer = BookCreateSerializer(data=request.data)

        # ── 2. 驗證資料（觸發 field 驗證 + validate() 業務邏輯驗證）
        #       raise_exception=True：驗證失敗時直接回傳 400，不需手動判斷 ──
        serializer.is_valid(raise_exception=True)

        # ── 3. 呼叫 Serializer.save()，內部會執行 create()，由 Service 層寫入 DB ──
        book = serializer.save()

        # ── 4. 用唯讀的 BookSerializer 回傳完整資料（含 id、created_at） ──
        return Response(BookSerializer(book).data, status=status.HTTP_201_CREATED)

    def get(self, request: Request, book_id: int) -> Response:
        # ── 1. 呼叫 Service 層取得單筆資料 ──
        book = self._get_book_or_400(book_id)

        # ── 2. 序列化後回傳 ──
        serializer = BookSerializer(book)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request: Request, book_id: int) -> Response:
        # ── 1. 取得要更新的 instance ──
        book = self._get_book_or_400(book_id)

        # ── 2. 將 instance 與 request.data 一起傳入 Serializer
        #       instance 的存在告訴 Serializer 這是「更新」操作 ──
        serializer = BookUpdateSerializer(book, data=request.data)

        # ── 3. 驗證（觸發 validate() 業務邏輯，此時 self.instance 已是 book） ──
        serializer.is_valid(raise_exception=True)

        # ── 4. 呼叫 Serializer.save()，內部執行 update()，由 Service 層更新 DB ──
        updated_book = serializer.save()

        # ── 5. 回傳更新後的完整資料 ──
        return Response(BookSerializer(updated_book).data, status=status.HTTP_200_OK)

    def delete(self, request: Request, book_id: int) -> Response:
        # ── 1. 取得要刪除的 instance ──
        book = self._get_book_or_400(book_id)

        # ── 2. 呼叫 Service 層刪除 ──
        BookService.delete_book(book)

        # ── 3. 刪除成功回傳 204 No Content ──
        return Response(status=status.HTTP_204_NO_CONTENT)
