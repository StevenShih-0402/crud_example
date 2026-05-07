"""
URL configuration for project_crud_example project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app.book.urls')),
    path('', include('app.user.urls')),
]
