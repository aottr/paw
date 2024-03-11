from django.contrib import admin
from .models import Category, Ticket, Comment, Template, Team, FileAttachment

# Register your models here.
admin.site.register(Category)
admin.site.register(Ticket)
admin.site.register(Comment)
admin.site.register(Template)
admin.site.register(Team)
admin.site.register(FileAttachment)
