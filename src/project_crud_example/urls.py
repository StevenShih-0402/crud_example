"""
URL configuration for project_crud_example project.
"""
from django.contrib import admin
from django.urls import path

from app.book.views.book_view import BookListView, BookDetailView

urlpatterns = [
    path('admin/', admin.site.urls),

    # 書本 API
    path('books/', BookListView.as_view(), name='book-list'),
    path('books/<int:book_id>/', BookDetailView.as_view(), name='book-detail'),
]
