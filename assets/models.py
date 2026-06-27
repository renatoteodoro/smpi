from django.db import models

from base.models import TimeStampedModel


class Equipment(TimeStampedModel):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Ativo'
        INACTIVE = 'inactive', 'Inativo'
        MAINTENANCE = 'maintenance', 'Em Manutenção'

    name = models.CharField('Nome', max_length=200)
    equipment_type = models.CharField('Tipo', max_length=100, help_text='Ex: motor, bomba, compressor')
    sector = models.CharField('Setor/Planta', max_length=200)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    description = models.TextField('Descrição', blank=True)
    image = models.ImageField(upload_to='equipment/', blank=True, null=True)

    class Meta:
        verbose_name = 'Equipamento'
        verbose_name_plural = 'Equipamentos'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def problem_count(self):
        from monitoring.models import SensorReading
        return SensorReading.objects.filter(
            measurement_point__equipment=self,
            status_class='problem'
        ).count()


class MeasurementPoint(TimeStampedModel):
    class Axis(models.TextChoices):
        X = 'X', 'X'
        Z = 'Z', 'Z'
        XZ = 'XZ', 'X e Z'

    equipment = models.ForeignKey(
        Equipment, on_delete=models.CASCADE, related_name='measurement_points'
    )
    name = models.CharField('Nome', max_length=200)
    axis = models.CharField('Eixo', max_length=5, choices=Axis.choices, default=Axis.XZ)
    sensor_type = models.CharField('Tipo de sensor', max_length=100, blank=True)
    location = models.CharField('Localização', max_length=200, blank=True)

    class Meta:
        verbose_name = 'Ponto de Medição'
        verbose_name_plural = 'Pontos de Medição'
        ordering = ['equipment', 'name']

    def __str__(self):
        return f'{self.equipment.name} — {self.name}'
