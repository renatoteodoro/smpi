from django.contrib import admin

from .models import Fault


@admin.register(Fault)
class FaultAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'is_problem', 'created_at')
    list_filter = ('is_problem',)
    search_fields = ('code', 'name')
    readonly_fields = ('is_problem', 'created_at', 'updated_at')
