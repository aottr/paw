from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import PawUser


@admin.register(PawUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Extended Data', {
         'fields': ('profile_picture', 'language', 'telegram_username')}),
    )
