from datetime import datetime, timezone as dt_timezone

from drf_spectacular.utils import OpenApiResponse, extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from app.user.models.access_token_blacklist_model import AccessTokenBlacklist


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["auth"],
        summary="登出",
        description=(
            "登出流程：\n"
            "1. 解析 Authorization header 中的 Access Token，將其 jti 加入自訂的 AccessTokenBlacklist。\n"
            "2. 若 body 帶有 `refresh`，將該 refresh token 加入 simplejwt 內建黑名單。"
        ),
        request=inline_serializer(
            name="LogoutRequest",
            fields={
                "refresh": serializers.CharField(
                    required=False,
                    help_text="可選；若提供，會將該 refresh token 加入黑名單。",
                ),
            },
        ),
        responses={204: OpenApiResponse(description="登出成功，無回傳內容。")},
    )
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
