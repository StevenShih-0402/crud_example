from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import authenticate


class LoginView(APIView):
    """
    POST /auth/login/

    接收 username + password，驗證成功後回傳 access token 與 refresh token。
    """

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response(
                {"detail": "帳號或密碼錯誤。"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # RefreshToken.for_user() 會同時建立 access token
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    """
    POST /auth/logout/

    接收 refresh token，將其加入黑名單使其失效（登出）。
    需要攜帶有效的 access token 才能呼叫。
    """

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "請提供 refresh token。"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            # blacklist() 將 token 存入黑名單，之後無法再用來換 access token
            token.blacklist()
        except TokenError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)


# TokenRefreshView 是 SimpleJWT 內建的 View，直接重新導出即可
# POST /auth/token/refresh/  →  接收 refresh 換發新的 access token
