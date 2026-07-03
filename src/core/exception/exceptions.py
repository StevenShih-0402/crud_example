from rest_framework import status
from rest_framework.exceptions import APIException

from core.enum.error_enum import ErrorEnum


class BusinessException(APIException):
    """業務邏輯例外基底。

    繼承 DRF APIException，使其能自然流經 DRF 例外處理流程並帶有
    status_code / default_detail / default_code。各業務例外請繼承本類並覆寫屬性。
    """

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = ErrorEnum.BUSINESS_ERROR.value
    default_code = ErrorEnum.BUSINESS_ERROR.name


class ResourceNotFoundError(BusinessException):
    """查無指定資源（404）。"""

    status_code = status.HTTP_404_NOT_FOUND
    default_detail = ErrorEnum.RESOURCE_NOT_FOUND.value
    default_code = ErrorEnum.RESOURCE_NOT_FOUND.name


class DuplicateResourceError(BusinessException):
    """資源重複（409）。"""

    status_code = status.HTTP_409_CONFLICT
    default_detail = ErrorEnum.DUPLICATE_RESOURCE.value
    default_code = ErrorEnum.DUPLICATE_RESOURCE.name
