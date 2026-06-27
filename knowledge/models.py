from django.db import models
from pgvector.django import VectorField

from base.models import TimeStampedModel
from faults.models import Fault

EMBEDDING_DIM = 384  # paraphrase-multilingual-MiniLM-L12-v2


class KnowledgeDocument(TimeStampedModel):
    title = models.CharField('Título', max_length=300)
    file = models.FileField(upload_to='knowledge/', blank=True, null=True)
    fault = models.ForeignKey(
        Fault, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='documents', verbose_name='Defeito associado'
    )
    tags = models.CharField('Tags', max_length=500, blank=True)
    description = models.TextField('Descrição', blank=True)
    is_ingested = models.BooleanField('Ingerido', default=False)

    class Meta:
        verbose_name = 'Documento Orientativo'
        verbose_name_plural = 'Documentos Orientativos'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class DocumentChunk(TimeStampedModel):
    document = models.ForeignKey(
        KnowledgeDocument, on_delete=models.CASCADE, related_name='chunks'
    )
    content = models.TextField()
    embedding = VectorField(dimensions=EMBEDDING_DIM, null=True, blank=True)
    chunk_index = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Chunk de Documento'
        verbose_name_plural = 'Chunks de Documento'
        ordering = ['document', 'chunk_index']

    def __str__(self):
        return f'{self.document.title} — chunk {self.chunk_index}'
