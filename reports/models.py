from django.db import models

from base.models import TimeStampedModel


class ReportRequest(TimeStampedModel):
    class Format(models.TextChoices):
        PDF = 'pdf', 'PDF'
        CSV = 'csv', 'CSV'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Aguardando'
        PROCESSING = 'processing', 'Processando'
        DONE = 'done', 'Concluído'
        FAILED = 'failed', 'Falhou'

    requested_by = models.ForeignKey(
        'accounts.User', on_delete=models.CASCADE, related_name='reports'
    )
    format = models.CharField(max_length=10, choices=Format.choices)
    filters = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    file = models.FileField(upload_to='reports/', null=True, blank=True)
    error = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Relatório'
        verbose_name_plural = 'Relatórios'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.format.upper()} — {self.requested_by.email} — {self.status}'
