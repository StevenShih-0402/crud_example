import logging

from django.utils import timezone
from drf_spectacular.contrib.rest_framework_simplejwt import SimpleJWTScheme
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken

from app.user.models.access_token_blacklist_model import AccessTokenBlacklist

logger = logging.getLogger(__name__)


class BlacklistJWTAuthentication(JWTAuthentication):
    def get_validated_token(self, raw_token):
        token = super().get_validated_token(raw_token)
        jti = token.get("jti")
        if jti and AccessTokenBlacklist.objects.filter(jti=jti, expires_at__gt=timezone.now()).exists():
            # 已登出的 token 又被拿來用，可能只是前端沒清乾淨，
            # 但連續出現就值得警覺，屬於資安上該留紀錄的事件
            logger.warning("已撤銷的 Access Token 嘗試存取：jti=%s", jti)
            raise InvalidToken("Token 已被撤銷")
        return token


class BlacklistJWTScheme(SimpleJWTScheme):
    """讓 drf-spectacular 知道如何在 OpenAPI schema 中描述自訂的 JWT 驗證類別。"""

    target_class = "app.user.authentication.BlacklistJWTAuthentication"
    name = "jwtAuth"
