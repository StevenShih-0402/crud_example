from django.db import models as model


class ErrorEnum(model.TextChoices):
    """集中管理錯誤訊息常數(value = 繁中訊息, label = 用途說明)。

    對齊 core.enum.swagger_enum.SwaggerEnum 的 TextChoices 慣例。
    """

    RESOURCE_NOT_FOUND = "查無此資料。", "資源不存在(404)"
    DUPLICATE_RESOURCE = "資料已存在，請勿重複建立。", "資源重複(409)"
    BUSINESS_ERROR = "請求處理失敗。", "業務邏輯錯誤(預設 400)"
    UNAUTHORIZED = "尚未通過身分驗證，請先登入。", "未授權(401)"
    SERVER_ERROR = "伺服器發生未預期的錯誤。", "伺服器錯誤(500)"
