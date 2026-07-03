from django.http import JsonResponse
from rest_framework import status

from core.enum.error_enum import ErrorEnum


def build_unauthorized_envelope(detail=None, code=ErrorEnum.UNAUTHORIZED.name):
    """組出 401 未授權的統一格式 {code, msg, data}。

    code 為語意化業務錯誤碼字串（預設取 ErrorEnum.UNAUTHORIZED.name，也可帶入
    DRF 例外的 default_code，如 "not_authenticated" / "authentication_failed" /
    "token_not_valid"）；HTTP 401 由 response 的 status 承載。
    """
    return {
        "code": code,
        "msg": ErrorEnum.UNAUTHORIZED.value,
        "data": {"detail": str(detail)} if detail else {},
    }


def unauthorized_view(request, exception=None):
    """自訂 401 錯誤頁面 View。

    - 可作為 URL path 目標直接存取（GET /error/401/）。
    - 也供 Global Exception Handler 在偵測到 401 時委派呼叫（透過
      build_unauthorized_envelope）。
    """
    return JsonResponse(
        build_unauthorized_envelope(),
        status=status.HTTP_401_UNAUTHORIZED,
        json_dumps_params={"ensure_ascii": False},
    )
