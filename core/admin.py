from django.contrib import admin

from .models import Task


class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'due_date', 'owner', 'created_at')
    list_filter = ('status',)
    search_fields = ('title',)


admin.site.register(Task, TaskAdmin)
