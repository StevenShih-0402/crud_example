from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from app.user.models.user_model import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("額外資訊", {"fields": ("phone",)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("額外資訊", {"fields": ("phone",)}),
    )
