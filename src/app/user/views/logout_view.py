from datetime import datetime, timezone as dt_timezone

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from app.user.models.access_token_blacklist_model import AccessTokenBlacklist


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 將 Access Token 加入黑名單
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            raw_access_token = auth_header.split(" ")[1]
            access_token = AccessToken(raw_access_token)
            jti = access_token["jti"]
            expires_at = datetime.fromtimestamp(access_token["exp"], tz=dt_timezone.utc)
            AccessTokenBlacklist.objects.get_or_create(jti=jti, defaults={"expires_at": expires_at})

        # 將 Refresh Token 加入 simplejwt 黑名單
        refresh_token = request.data.get("refresh")
        if refresh_token:
            try:
                RefreshToken(refresh_token).blacklist()
            except TokenError:
                pass

        return Response(status=status.HTTP_204_NO_CONTENT)
