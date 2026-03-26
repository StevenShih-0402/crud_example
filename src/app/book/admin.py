from django.contrib import admin
from app.models.book_model import Book

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('id', 'book_name', 'description', 'writer', 'publish_date')
    search_fields = ('book_name', 'writer')
    ordering = ('-publish_date', '-id')