from django.conf import settings
from django.db import models

from base.models import TimeStampedModel


class ChatSession(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_sessions'
    )
    title = models.CharField(max_length=200, default='Nova conversa')

    class Meta:
        verbose_name = 'Sessão de Chat'
        ordering = ['-updated_at']
        unique_together = [('user', 'title')]

    def __str__(self):
        return f'{self.user.email} — {self.title}'


class ChatMessage(TimeStampedModel):
    class Role(models.TextChoices):
        USER = 'user', 'Usuário'
        ASSISTANT = 'assistant', 'Assistente'
        SYSTEM = 'system', 'Sistema'

    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20, choices=Role.choices)
    content = models.TextField()

    class Meta:
        verbose_name = 'Mensagem de Chat'
        ordering = ['created_at']

    def __str__(self):
        return f'{self.role}: {self.content[:50]}'
