from django.db import models

from base.models import TimeStampedModel


class DashboardSnapshot(TimeStampedModel):
    """Periodic summary computed by Celery beat for the main dashboard."""
    total_readings = models.IntegerField(default=0)
    problem_readings = models.IntegerField(default=0)
    state_readings = models.IntegerField(default=0)
    pending_readings = models.IntegerField(default=0)
    total_prescriptions = models.IntegerField(default=0)
    grounded_prescriptions = models.IntegerField(default=0)
    data = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = 'Snapshot do Dashboard'
        ordering = ['-created_at']

    def __str__(self):
        return f'Snapshot {self.created_at}'
