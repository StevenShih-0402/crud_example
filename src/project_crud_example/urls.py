"""
URL configuration for project_crud_example project.
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from app.book.views.book_view import BookViewSet

router = DefaultRouter()
router.register("books", BookViewSet, basename="book")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
]
