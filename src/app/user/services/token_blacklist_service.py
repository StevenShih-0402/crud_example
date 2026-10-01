import logging
import time

from core.redis_client import redis_client

logger = logging.getLogger(__name__)


class TokenBlacklistService:
    """
    Access Token 黑名單（存放於 Redis）。

    每個被撤銷的 token 對應一個 key：`jwt:blacklist:access:<jti>`，
    並把 TTL 設成「距離 token 過期還剩幾秒」。token 過期後本來就無法通過驗證，
    黑名單紀錄也就沒有保留的必要——交給 Redis 自動刪除，不必再寫排程清理過期資料。
    """

    KEY_PREFIX = "jwt:blacklist:access:"

    @classmethod
    def _key(cls, jti: str) -> str:
        return f"{cls.KEY_PREFIX}{jti}"

    @classmethod
    def add(cls, jti: str, exp: int):
        """將 jti 加入黑名單；exp 為 token payload 中的過期時間（Unix timestamp）。"""
        ttl = exp - int(time.time())
        if ttl <= 0:
            # 已過期的 token 驗證時本來就會被擋，不必佔用 Redis 空間
            logger.debug("Access Token 已過期，不需加入黑名單：jti=%s", jti)
            return
        # SET key value EX ttl：寫入並同時設定存活秒數（重複登出只會覆寫，不會出錯）
        redis_client.set(cls._key(jti), 1, ex=ttl)

    @classmethod
    def is_blacklisted(cls, jti: str) -> bool:
        # EXISTS 回傳存在的 key 數量；過期的 key 已被 Redis 刪除，自然回傳 0
        return redis_client.exists(cls._key(jti)) > 0
