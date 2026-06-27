from django.contrib import admin

from .models import WhatsAppMessage


@admin.register(WhatsAppMessage)
class WhatsAppMessageAdmin(admin.ModelAdmin):
    list_display = ('direction', 'phone', 'content_preview', 'created_at')
    list_filter = ('direction',)
    readonly_fields = ('raw_payload', 'message_id')

    def content_preview(self, obj):
        return obj.content[:80]
    content_preview.short_description = 'Mensagem'
