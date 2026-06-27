from django.db import models
from pgvector.django import VectorField

from base.models import TimeStampedModel
from assets.models import MeasurementPoint
from faults.models import Fault

FEATURE_COLUMNS = [
    'z_rms_velocity_mm_s', 'x_rms_velocity_mm_s', 'temperature_c',
    'z_peak_acceleration_g', 'x_peak_acceleration_g',
    'z_peak_vel_comp_freq_hz', 'x_peak_vel_comp_freq_hz',
    'z_rms_acceleration_g', 'x_rms_acceleration_g',
    'z_kurtosis', 'x_kurtosis',
    'z_crest_factor', 'x_crest_factor',
    'z_peak_velocity_mm_s', 'x_peak_velocity_mm_s',
    'z_high_freq_rms_accel_g', 'x_high_freq_rms_accel_g',
    'rpm',
]
FEATURE_DIM = len(FEATURE_COLUMNS)  # 18


class SensorReading(TimeStampedModel):
    class StatusClass(models.TextChoices):
        PENDING = 'pending', 'Aguardando análise'
        STATE = 'state', 'Estado operacional'
        PROBLEM = 'problem', 'Problema detectado'

    measurement_point = models.ForeignKey(
        MeasurementPoint, on_delete=models.PROTECT, related_name='readings'
    )
    external_id = models.BigIntegerField(
        'ID externo', unique=True, db_index=True, null=True, blank=True,
        help_text='ID de origem para idempotência'
    )
    metrics = models.JSONField('Métricas brutas', help_text='Todas as colunas do evento original')
    feature_vector = VectorField(dimensions=FEATURE_DIM, null=True, blank=True)
    fault = models.ForeignKey(
        Fault, on_delete=models.SET_NULL, null=True, blank=True, related_name='readings'
    )
    status_class = models.CharField(
        max_length=10, choices=StatusClass.choices, default=StatusClass.PENDING
    )
    rpm = models.FloatField(null=True, blank=True)
    event_created_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Leitura de Sensor'
        verbose_name_plural = 'Leituras de Sensor'
        ordering = ['-event_created_at']

    def __str__(self):
        return f'Leitura {self.external_id} @ {self.measurement_point}'
