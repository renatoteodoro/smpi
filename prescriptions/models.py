from django.db import models

from base.models import TimeStampedModel
from faults.models import Fault
from knowledge.models import DocumentChunk
from monitoring.models import SensorReading


class Prescription(TimeStampedModel):
    sensor_reading = models.OneToOneField(
        SensorReading, on_delete=models.CASCADE, related_name='prescription'
    )
    fault = models.ForeignKey(
        Fault, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='prescriptions'
    )
    defect_type = models.CharField('Tipo de defeito', max_length=200, blank=True)
    occurrences_count = models.IntegerField('Qtd. ocorrências', default=0)
    occurrences_frequency = models.CharField('Frequência', max_length=300, blank=True)
    instructions = models.TextField('Instruções (Markdown)', blank=True)
    source_chunks = models.ManyToManyField(DocumentChunk, blank=True, related_name='prescriptions')
    is_grounded = models.BooleanField(
        'Fundamentada', default=True,
        help_text='False = acionou regra de guarda (sem documentação)'
    )
    pipeline_log = models.JSONField('Log do pipeline', default=dict, blank=True)

    class Meta:
        verbose_name = 'Prescrição'
        verbose_name_plural = 'Prescrições'
        ordering = ['-created_at']

    def __str__(self):
        return f'Prescrição para leitura #{self.sensor_reading_id}'
