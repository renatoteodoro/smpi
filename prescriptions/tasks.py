from celery import shared_task


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def run_prescription_pipeline(self, reading_id: int):
    """Run the full LangGraph prescriptive pipeline for a SensorReading."""
    try:
        from accounts.models import User
        from monitoring.models import SensorReading
        from notifications.models import Notification
        from .pipeline import execute_pipeline

        reading = SensorReading.objects.get(pk=reading_id)
        prescription = execute_pipeline(reading)

        for user in User.objects.filter(role__in=['admin', 'maintenance'], is_active=True):
            Notification.objects.create(
                user=user,
                title='Prescrição gerada',
                message=(
                    f'Análise do evento #{reading.external_id or reading_id} concluída — '
                    f'{prescription.defect_type or "estado"}.'
                ),
                level='success' if prescription.is_grounded else 'warning',
                link=f'/prescriptions/{prescription.pk}/',
            )
    except Exception as exc:
        raise self.retry(exc=exc)
