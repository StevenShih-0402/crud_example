import logging

from django.core.exceptions import (
    ObjectDoesNotExist,
    PermissionDenied as DjangoPermissionDenied,
    ValidationError as DjangoValidationError,
)
from rest_framework import status
from rest_framework.exceptions import (
    NotFound,
    PermissionDenied,
    ValidationError,
)
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from core.enum.error_enum import ErrorEnum
from core.exception.exceptions import BusinessException
from core.exception.response import build_error_envelope
from core.exception.views.error_view import build_unauthorized_envelope

logger = logging.getLogger(__name__)


def _translate_django_exception(exc):
    """把 django.core.exceptions 家族轉成 DRF 認得的例外。

    DRF 預設 handler 只認得 Http404 與 django 的 PermissionDenied，
    其餘（ObjectDoesNotExist、django ValidationError）會直接變成 500，
    這裡先行轉譯成對應的 DRF 例外。
    """
    if isinstance(exc, ObjectDoesNotExist):
        return NotFound()
    if isinstance(exc, DjangoValidationError):
        return ValidationError(exc.messages)
    if isinstance(exc, DjangoPermissionDenied):
        return PermissionDenied()
    return exc


def custom_exception_handler(exc, context):
    """Global Exception Handler：全域統一錯誤回應。

    流程：
    1. 先轉譯 django.core.exceptions → DRF 例外。
    2. 交給 DRF 預設 handler 取得 response（可接住 APIException 子類，
       含自定義 BusinessException、NotAuthenticated、AuthenticationFailed、
       InvalidToken 等）。
    3. 401 未授權：委派給自訂 401 View 模組產生 envelope。
    4. BusinessException 系列：msg 固定用 Enum 預設訊息，動態內容放 data。
    5. 其他錯誤：包成統一的 {code, msg, data} envelope。
    6. 未被接住的例外（response is None，例如原生 Python 例外）→ 500 兜底。
    """
    exc = _translate_django_exception(exc)

    response = drf_exception_handler(exc, context)

    # 未被 DRF 接住（例如原生 Python 例外）→ 500 兜底，避免裸露堆疊
    if response is None:
        # 本 handler 一律回傳 Response，DRF 便不會再往上拋，
        # Django 內建的 django.request logger 也就看不到這個例外。
        # 若這裡不記錄，真正的系統錯誤會完全靜默、連堆疊都不留。
        # logger.exception 等同 logger.error(..., exc_info=True)，會附上完整 traceback。
        logger.exception("未預期的例外，回傳 500：view=%s", context.get("view"))
        envelope = build_error_envelope(
            ErrorEnum.SERVER_ERROR.name,
            {"detail": ErrorEnum.SERVER_ERROR.value},
        )
        return Response(envelope, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 401 未授權：委派給自訂 401 View 模組
    # 沿用原 response（而非 new 一個）以保留 headers，
    # 否則 BasicAuthentication 的 WWW-Authenticate 挑戰標頭會遺失，
    # 導致瀏覽器不會跳出登入框、直接顯示裸 401。
    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        detail = response.data.get("detail") if isinstance(response.data, dict) else None
        code = getattr(exc, "default_code", ErrorEnum.UNAUTHORIZED.name)
        response.data = build_unauthorized_envelope(detail, code)
        return response

    # 自訂 BusinessException 系列：msg 固定用類別預設的 Enum 訊息，
    # 實際拋出時帶的動態內容（例如帶 id 的訊息）保留在 data，不混進 msg。
    if isinstance(exc, BusinessException):
        detail = response.data.get("detail") if isinstance(response.data, dict) else None
        response.data = {
            "code": exc.default_code,
            "msg": exc.default_detail,
            "data": {"detail": str(detail)} if detail else {},
        }
        return response

    # 其他錯誤：統一包成 {code, msg, data}，code 取 DRF 例外的 default_code
    #（如 ValidationError→"invalid"、NotFound→"not_found"），無則退回 "error"
    code = getattr(exc, "default_code", "error")
    response.data = build_error_envelope(code, response.data)
    return response
