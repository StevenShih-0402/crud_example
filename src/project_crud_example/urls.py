"""
URL configuration for project_crud_example project.
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAdminUser

from core.exception.views.error_view import unauthorized_view

# 文件頁面共用：Basic Auth + 管理員權限（Django superuser 預設 is_staff=True）
_DOCS_AUTH = [BasicAuthentication]
_DOCS_PERM = [IsAdminUser]

schema_view = SpectacularAPIView.as_view(
    authentication_classes=_DOCS_AUTH,
    permission_classes=_DOCS_PERM,
)
swagger_view = SpectacularSwaggerView.as_view(
    url_name="schema",
    authentication_classes=_DOCS_AUTH,
    permission_classes=_DOCS_PERM,
)
redoc_view = SpectacularRedocView.as_view(
    url_name="schema",
    authentication_classes=_DOCS_AUTH,
    permission_classes=_DOCS_PERM,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app.book.urls')),
    path('', include('app.user.urls')),

    # OpenAPI / 文件頁面（需要 admin 帳密 Basic Auth 登入）
    path('api/schema/', schema_view, name='schema'),
    path('api/schema/swagger-ui/', swagger_view, name='swagger-ui'),
    path('api/schema/redoc/', redoc_view, name='redoc'),

    # 自訂 401 錯誤頁面（可直接存取，亦供 Global Exception Handler 委派）
    path('error/401/', unauthorized_view, name='unauthorized'),
]
