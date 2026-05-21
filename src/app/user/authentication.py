from django.utils import timezone
from drf_spectacular.contrib.rest_framework_simplejwt import SimpleJWTScheme
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken

from app.user.models.access_token_blacklist_model import AccessTokenBlacklist


class BlacklistJWTAuthentication(JWTAuthentication):
    def get_validated_token(self, raw_token):
        token = super().get_validated_token(raw_token)
        jti = token.get("jti")
        if jti and AccessTokenBlacklist.objects.filter(jti=jti, expires_at__gt=timezone.now()).exists():
            raise InvalidToken("Token 已被撤銷")
        return token


class BlacklistJWTScheme(SimpleJWTScheme):
    """讓 drf-spectacular 知道如何在 OpenAPI schema 中描述自訂的 JWT 驗證類別。"""

    target_class = "app.user.authentication.BlacklistJWTAuthentication"
    name = "jwtAuth"
