from django.contrib import admin

from .models import SensorReading


@admin.register(SensorReading)
class SensorReadingAdmin(admin.ModelAdmin):
    list_display = ('external_id', 'measurement_point', 'fault', 'status_class', 'rpm', 'event_created_at')
    list_filter = ('status_class', 'fault', 'measurement_point__equipment')
    search_fields = ('external_id', 'measurement_point__name')
    readonly_fields = ('feature_vector', 'metrics', 'created_at', 'updated_at')
    date_hierarchy = 'event_created_at'
