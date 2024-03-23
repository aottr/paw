from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import PawUser, MailTemplate, GoogleSSOUser


@admin.register(PawUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Extended Data', {
         'fields': ('profile_picture', 'language', 'telegram_username')}),
    )

@admin.register(MailTemplate)
class MailTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'event', 'language')
    list_filter = ('event', 'language')

@admin.register(GoogleSSOUser)
class GoogleSSOUserAdmin(admin.ModelAdmin):
    list_display = ('paw_user', 'google_id')