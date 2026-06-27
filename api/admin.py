from django.contrib import admin

from .models import ApiKey


@admin.register(ApiKey)
class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'is_active', 'last_used_at', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'user__email')
    readonly_fields = ('key', 'last_used_at', 'created_at', 'updated_at')
