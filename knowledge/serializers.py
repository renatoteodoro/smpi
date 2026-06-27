from rest_framework import serializers

from .models import DocumentChunk, KnowledgeDocument


class DocumentChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentChunk
        fields = ('id', 'chunk_index', 'content', 'document')


class KnowledgeDocumentSerializer(serializers.ModelSerializer):
    chunk_count = serializers.SerializerMethodField()

    def get_chunk_count(self, obj):
        return obj.chunks.count()

    class Meta:
        model = KnowledgeDocument
        fields = ('id', 'title', 'fault', 'tags', 'description', 'is_ingested', 'chunk_count', 'created_at')
        read_only_fields = ('is_ingested',)
