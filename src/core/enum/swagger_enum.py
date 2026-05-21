from django.db import models as model


class SwaggerEnum(model.TextChoices):
    BOOK_LIST_SUMMARY = "書本列表", "Book GET(list) API 簡介"
    BOOK_LIST_DESCRIPTION = "取得書本列表，依建立時間（created_at）由新到舊排序，並使用 PageNumberPagination 分頁。", "Book GET(list) API 詳細說明"
    BOOK_CREATE_SUMMARY = "新增書本", "Book POST API 簡介"
    BOOK_CREATE_DESCRIPTION = "建立新書本。\n- 由 BookCreateSerializer.validate() 委派 BookService 檢查書名唯一性。\n- 由 BookCreateSerializer.create() 委派 BookService 寫入資料並設定 created_at。", "Book POST API 詳細說明"
    BOOK_RETRIEVE_SUMMARY = "取得單一書本", "Book GET(retrieve) API 簡介"
    BOOK_RETRIEVE_DESCRIPTION = "依主鍵（id）取得單一書本詳細資料。", "Book GET(retrieve) API 詳細說明"
    BOOK_UPDATE_SUMMARY = "更新書本（全部欄位）", "Book PUT API 簡介"
    BOOK_UPDATE_DESCRIPTION = "以 PUT 全量更新書本。\n- 由 BookUpdateSerializer.validate() 委派 BookService 檢查書名唯一性（排除自身）。\n- 由 BookUpdateSerializer.update() 委派 BookService 更新資料並設定 updated_at。", "Book PUT API 詳細說明"
    BOOK_PARTIAL_UPDATE_SUMMARY = "部分更新書本", "Book PATCH API 簡介"
    BOOK_PARTIAL_UPDATE_DESCRIPTION = "以 PATCH 部分更新書本欄位，驗證與寫入流程同 update。", "Book PATCH API 詳細說明"
    BOOK_DESTROY_SUMMARY = "刪除書本", "Book DELETE API 簡介"
    BOOK_DESTROY_DESCRIPTION = "依主鍵（id）刪除書本，刪除成功回傳 204 No Content。", "Book DELETE API 詳細說明"
