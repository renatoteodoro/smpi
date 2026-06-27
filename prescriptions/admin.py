from django.contrib import admin

from .models import Prescription


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('sensor_reading', 'fault', 'defect_type', 'occurrences_count', 'is_grounded', 'created_at')
    list_filter = ('is_grounded', 'fault')
    search_fields = ('defect_type', 'sensor_reading__external_id')
    readonly_fields = ('sensor_reading', 'pipeline_log', 'source_chunks', 'created_at', 'updated_at')
    filter_horizontal = ('source_chunks',)
