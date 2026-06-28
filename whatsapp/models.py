from django.db import models

from base.models import TimeStampedModel


class WhatsAppMessage(TimeStampedModel):
    class Direction(models.TextChoices):
        INBOUND = 'inbound', 'Recebida'
        OUTBOUND = 'outbound', 'Enviada'

    direction = models.CharField(max_length=10, choices=Direction.choices)
    phone = models.CharField(max_length=30)
    reply_jid = models.CharField(max_length=100, blank=True)  # remoteJid para envio de resposta
    message_id = models.CharField(max_length=200, unique=True)
    content = models.TextField()
    raw_payload = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = 'Mensagem WhatsApp'
        verbose_name_plural = 'Mensagens WhatsApp'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.direction} — {self.phone} — {self.content[:40]}'
