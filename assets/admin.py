from django.contrib import admin

from .models import Equipment, MeasurementPoint


class MeasurementPointInline(admin.TabularInline):
    model = MeasurementPoint
    extra = 1
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'equipment_type', 'sector', 'status', 'created_at')
    list_filter = ('status', 'equipment_type', 'sector')
    search_fields = ('name', 'sector')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [MeasurementPointInline]


@admin.register(MeasurementPoint)
class MeasurementPointAdmin(admin.ModelAdmin):
    list_display = ('name', 'equipment', 'axis', 'sensor_type', 'created_at')
    list_filter = ('axis', 'equipment')
    search_fields = ('name', 'equipment__name')
    readonly_fields = ('created_at', 'updated_at')
