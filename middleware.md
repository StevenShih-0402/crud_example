class CustomResponseMiddleware(MiddlewareMixin):
    """
    統一 API 回傳格式的 middleware
    """

    @staticmethod
    def process_response(request, response):
        # 只處理 HTTPS 請求，非 API 回應 (例如 admin 或 HTML)就不處理

        # 如果 API_PREFIX 不正確，就不包裝直接回傳
        logger.info(NormalizeUtils.path_prefix("api/"))
        if not request.path.startswith(NormalizeUtils.path_prefix("api/")):
            return response

        # 如果已經是統一格式，避免重複包裝
        if isinstance(response, JsonResponse):
            data = json.loads(response.content.decode())
            if {"code", "msg", "data"}.issubset(data.keys()):
                return response

        # Django 原生 View 可能是 HttpResponse，不處理
        if not isinstance(response, Response) and not hasattr(response, "data"):
            return response

        # 非 DRF Response 物件（如 Static files 等）直接跳過
        if not hasattr(response, "data"):
            return response

        # 成功回傳 (2xx)
        is_success = status.is_success(response.status_code)

        code = response.status_code
        msg = "SUCCESS" if is_success else "FAILURE"
        data = {}

        if is_success:
            data = response.data if response.data else {}
        else:
            error_data = response.data
            # 保留原始 error data，方便 client 取得詳細錯誤資訊
            if isinstance(error_data, dict):
                data = error_data
                if "detail" in error_data:
                    msg = error_data["detail"]
                else:
                    messages = []
                    for field, errors in error_data.items():
                        if isinstance(errors, list):
                            messages.append(f"{field}: {', '.join(errors)}")
                        else:
                            messages.append(f"{field}: {errors}")
                    msg = "; ".join(messages) if messages else "請求處理失敗"
            elif isinstance(error_data, list):
                data = error_data
                msg = "; ".join(str(item) for item in error_data)
            else:
                msg = str(error_data)

        final_response = {"code": code, "msg": msg, "data": data}

        # 成功請求一律回傳 HTTP 200
        if is_success:
            return JsonResponse(final_response, status=200, json_dumps_params={"ensure_ascii": False})
        else:
            return JsonResponse(final_response, status=code, json_dumps_params={"ensure_ascii": False})