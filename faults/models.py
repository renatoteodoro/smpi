from django.db import models

from base.models import TimeStampedModel

STATE_CODES = frozenset({'normal', 'baseline', 'teste', 'acelerando', 'motor_desligado'})


class Fault(TimeStampedModel):
    code = models.CharField(
        'Código', max_length=100, unique=True,
        help_text='Ex: cocked_rotor_2, normal, unbalance'
    )
    name = models.CharField('Nome', max_length=200)
    is_problem = models.BooleanField(
        'É problema?', default=True,
        help_text='False = estado operacional normal'
    )
    description = models.TextField('Descrição', blank=True)

    class Meta:
        verbose_name = 'Defeito/Estado'
        verbose_name_plural = 'Defeitos/Estados'
        ordering = ['-is_problem', 'code']

    def __str__(self):
        kind = 'Problema' if self.is_problem else 'Estado'
        return f'{self.code} ({kind})'

    def save(self, *args, **kwargs):
        self.is_problem = self.code.lower() not in STATE_CODES
        super().save(*args, **kwargs)
