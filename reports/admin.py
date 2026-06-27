from django.contrib import admin

from .models import ReportRequest


@admin.register(ReportRequest)
class ReportRequestAdmin(admin.ModelAdmin):
    list_display = ('requested_by', 'format', 'status', 'created_at')
    list_filter = ('format', 'status')
    readonly_fields = ('requested_by', 'filters', 'file', 'error', 'created_at', 'updated_at')
