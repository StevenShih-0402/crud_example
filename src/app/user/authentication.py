from django.utils import timezone
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
