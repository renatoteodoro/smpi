from django.contrib import admin

from .models import DashboardSnapshot


@admin.register(DashboardSnapshot)
class DashboardSnapshotAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'total_readings', 'problem_readings', 'total_prescriptions')
    readonly_fields = ('data', 'created_at', 'updated_at')
