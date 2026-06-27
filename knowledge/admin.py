from django.contrib import admin

from .models import DocumentChunk, KnowledgeDocument


class DocumentChunkInline(admin.TabularInline):
    model = DocumentChunk
    extra = 0
    readonly_fields = ('chunk_index', 'content', 'embedding')
    fields = ('chunk_index', 'content')
    can_delete = False
    max_num = 10
    show_change_link = False


@admin.register(KnowledgeDocument)
class KnowledgeDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'fault', 'is_ingested', 'chunk_count', 'created_at')
    list_filter = ('is_ingested', 'fault')
    search_fields = ('title', 'tags')
    readonly_fields = ('is_ingested', 'created_at', 'updated_at')
    inlines = [DocumentChunkInline]

    def chunk_count(self, obj):
        return obj.chunks.count()
    chunk_count.short_description = 'Chunks'


@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = ('document', 'chunk_index', 'content_preview', 'created_at')
    list_filter = ('document',)
    readonly_fields = ('created_at', 'updated_at')

    def content_preview(self, obj):
        return obj.content[:80] + '...' if len(obj.content) > 80 else obj.content
    content_preview.short_description = 'Conteúdo'
