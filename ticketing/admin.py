from django.contrib import admin
from .models import Category, Ticket, Comment, Template, Team, FileAttachment


admin.site.register(Category)

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'priority', 'category', 'created_at', 'updated_at')
    list_filter = ('status', 'priority', 'category')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

admin.site.register(Comment)
admin.site.register(Template)

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    filter_horizontal = ('members',)
admin.site.register(FileAttachment)
