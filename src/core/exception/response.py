"""共用的錯誤回應格式工具。

將錯誤內容統一拆解成可讀的 msg，並包成 {code, msg, data} envelope，
供 Global Exception Handler（core.exception.exception_handler）與統一回傳格式
middleware（core.middleware.response_format）共用，避免邏輯重複。
"""


def build_error_message(error_data):
    """從 DRF 錯誤內容拆出 (data, msg)。
    """
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


def build_error_envelope(code, error_data):
    """組出統一錯誤格式 {"code": code, "msg": msg, "data": data}。

    code 為語意化的業務錯誤碼字串（例如 "resource_not_found"、"server_error"），
    對齊各例外類別的 default_code；HTTP 狀態碼另由 response 的 status 承載。
    """
    data, msg = build_error_message(error_data)
    return {"code": code, "msg": msg, "data": data}
