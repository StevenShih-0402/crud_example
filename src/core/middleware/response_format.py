import json

from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework import status
from rest_framework.response import Response


class CustomResponseMiddleware(MiddlewareMixin):
    """
    統一 API 回傳格式的 middleware，將回應包成 code-msg-data：

        {
            "code": <原始 HTTP status code>,
            "msg":  "SUCCESS" 或錯誤訊息,
            "data": <原始回應內容>,
            "pagination": {            # 僅分頁回應才有
                "count": ...,
                "next": ...,
                "previous": ...
            }
        }

    - 成功（2xx）一律回 HTTP 200，原始狀態碼保留在 code。
    - 失敗維持原 HTTP 狀態碼，原始錯誤內容保留在 data。
    """

    # 文件 / schema / admin 等非業務路徑不包裝（包裝會破壞 Swagger UI）
    EXCLUDED_PREFIXES = ("/admin", "/api/schema")

    def process_response(self, request, response):
        # 非業務路徑（文件、後台）直接跳過
        if request.path.startswith(self.EXCLUDED_PREFIXES):
            return response

        # 已是統一格式，避免重複包裝
        if isinstance(response, JsonResponse):
            try:
                wrapped = json.loads(response.content.decode())
            except (ValueError, UnicodeDecodeError):
                return response
            if isinstance(wrapped, dict) and {"code", "msg", "data"}.issubset(wrapped.keys()):
                return response

        # 非 DRF Response（Django 原生 HttpResponse、靜態檔等）不處理
        if not isinstance(response, Response) and not hasattr(response, "data"):
            return response

        is_success = status.is_success(response.status_code)
        body = {"code": response.status_code, "msg": "SUCCESS" if is_success else "FAILURE", "data": {}}

        if is_success:
            data = response.data if response.data is not None else {}
            # 分頁回應：拆出 results 與分頁 meta（平級）
            if self._is_paginated(data):
                body["data"] = data["results"]
                body["pagination"] = {
                    "count": data["count"],
                    "next": data["next"],
                    "previous": data["previous"],
                }
            else:
                body["data"] = data
            http_status = status.HTTP_200_OK
        else:
            body["data"], body["msg"] = self._build_error(response.data)
            http_status = response.status_code

        return JsonResponse(body, status=http_status, json_dumps_params={"ensure_ascii": False})

    @staticmethod
    def _is_paginated(data):
        # 對應 StandardPageNumberPagination.get_paginated_response 的結構
        return isinstance(data, dict) and {"count", "next", "previous", "results"} <= data.keys()

    @staticmethod
    def _build_error(error_data):
        # 保留原始 error data，並組出可讀的 msg
        if isinstance(error_data, dict):
            if "detail" in error_data:
                return error_data, str(error_data["detail"])
            messages = []
            for field, errors in error_data.items():
                if isinstance(errors, list):
                    messages.append(f"{field}: {', '.join(str(e) for e in errors)}")
                else:
                    messages.append(f"{field}: {errors}")
            return error_data, "; ".join(messages) if messages else "請求處理失敗"
        if isinstance(error_data, list):
            return error_data, "; ".join(str(item) for item in error_data)
        return error_data, str(error_data)
