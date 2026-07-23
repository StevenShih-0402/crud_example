"""Logging 用的 request-scoped 上下文與 Filter。

Python logging 的 formatter 只能顯示 LogRecord 上既有的屬性，
但 trace_id 這種資訊是「進到 request 才知道」的，
不可能要求每個 logger 呼叫點都手動傳進來。

作法：
  1. 用 ContextVar 保存 request-scoped 資料（ContextVar 天生 thread / async 安全，
     不會像全域變數那樣讓多個 request 互相污染）。
  2. 用 logging.Filter 在每筆 LogRecord 產生時，把 ContextVar 的值補到 record 上，
     formatter 就能用 %(trace_id)s 印出來。

寫入端在 core.middleware.trace_id.TraceIDMiddleware。
"""

import logging
from contextvars import ContextVar

# 尚未進入 request（例如 manage.py 指令、開機期間的 log）時的預設值
trace_id_ctx: ContextVar[str] = ContextVar("trace_id", default="-")


class TraceIDFilter(logging.Filter):
    """為每筆 LogRecord 注入 trace_id。

    Filter 的回傳值決定該筆 log 是否要輸出，這裡固定回傳 True
    （只借用 filter() 的時機做欄位補值，不做過濾）。
    """

    def filter(self, record):
        record.trace_id = trace_id_ctx.get()
        return True
