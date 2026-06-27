from django.conf import settings
from django.db import models

from base.models import TimeStampedModel


class Notification(TimeStampedModel):
    """In-app notification delivered to a specific user.

    Created by Celery tasks upon completion of async operations
    (event analysis, prescription generation, document ingestion, etc.).
    """

    class Level(models.TextChoices):
        INFO = 'info', 'Info'
        SUCCESS = 'success', 'Sucesso'
        WARNING = 'warning', 'Aviso'
        ERROR = 'error', 'Erro'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    level = models.CharField(max_length=10, choices=Level.choices, default=Level.INFO)
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=500, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notificação'
        verbose_name_plural = 'Notificações'

    def __str__(self):
        return f'{self.user} — {self.title}'
