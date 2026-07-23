"""為每個 request 產生唯一 trace_id 的 middleware。

一次 request 通常會經過 View → Serializer → Service 等多層，各層都會寫 log；
多人同時使用時，log 交錯在一起就很難追蹤。
替每個 request 綁一組 trace_id，即可用 `grep <trace_id>` 把同一次請求的
所有 log 串成一條完整的執行軌跡。
"""

import uuid

from core.logging_filters import trace_id_ctx


class TraceIDMiddleware:
    """把 trace_id 寫入 ContextVar，並回寫到回應標頭。

    - 若 client 帶了 X-Trace-ID（例如前端或上游服務已產生），沿用該值，
      讓跨服務的 log 可以串接；否則自行產生 UUID。
    - 回應一律附上 X-Trace-ID，使用者回報問題時可直接提供此 id 供查詢。
    - finally 一定要 reset，避免 ContextVar 殘留、污染同一 thread 的下一個 request。
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        trace_id = request.headers.get("X-Trace-ID") or str(uuid.uuid4())
        token = trace_id_ctx.set(trace_id)
        request.trace_id = trace_id
        try:
            response = self.get_response(request)
            response["X-Trace-ID"] = trace_id
            return response
        finally:
            trace_id_ctx.reset(token)
