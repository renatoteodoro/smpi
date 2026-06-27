import secrets

from django.conf import settings
from django.db import models

from base.models import TimeStampedModel


class ApiKey(TimeStampedModel):
    """System API key used for authenticating ingest endpoints (X-Api-Key header).

    Keys are generated with secrets.token_urlsafe(48) on first save.
    The key is shown once in the admin — store it securely on the client side.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='api_keys',
        null=True,
        blank=True,
        help_text='Usuário vinculado a esta chave (opcional para chaves de sistema).',
    )
    name = models.CharField(max_length=100, help_text='Descrição legível da chave.')
    key = models.CharField(max_length=64, unique=True, db_index=True)
    is_active = models.BooleanField(default=True)
    last_used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'API Key'
        verbose_name_plural = 'API Keys'

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = secrets.token_urlsafe(48)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name} ({self.key[:8]}...)'
