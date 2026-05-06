"""
URL configuration for project_crud_example project.
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from app.book.views.book_view import BookListView, BookDetailView
from app.user.views.auth_view import LoginView, LogoutView
from app.user.views.user_view import UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('admin/', admin.site.urls),

    # 書本 API
    path('books/', BookListView.as_view(), name='book-list'),
    path('books/<int:book_id>/', BookDetailView.as_view(), name='book-detail'),

    # 使用者 CRUD（ModelViewSet via Router）
    path('', include(router.urls)),

    # 認證 API
    path('auth/login/', LoginView.as_view(), name='auth-login'),
    path('auth/logout/', LogoutView.as_view(), name='auth-logout'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='auth-token-refresh'),
]
