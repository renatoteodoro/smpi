from celery import shared_task


@shared_task(bind=True, max_retries=2, default_retry_delay=30)
def generate_report(self, report_id: int):
    """Build the report file and notify the user."""
    from .models import ReportRequest
    from monitoring.models import SensorReading
    from django.core.files.base import ContentFile
    from notifications.models import Notification

    report = ReportRequest.objects.get(pk=report_id)
    report.status = 'processing'
    report.save(update_fields=['status', 'updated_at'])

    try:
        qs = SensorReading.objects.all()
        if report.filters.get('status'):
            qs = qs.filter(status_class=report.filters['status'])
        if report.filters.get('fault'):
            qs = qs.filter(fault__code=report.filters['fault'])
        if report.filters.get('date_from'):
            qs = qs.filter(event_created_at__date__gte=report.filters['date_from'])
        if report.filters.get('date_to'):
            qs = qs.filter(event_created_at__date__lte=report.filters['date_to'])

        if report.format == 'csv':
            from .generators import generate_csv
            content = generate_csv(qs)
            filename = f'relatorio_{report.pk}.csv'
        else:
            from .generators import generate_pdf
            content = generate_pdf(qs)
            filename = f'relatorio_{report.pk}.pdf'

        report.file.save(filename, ContentFile(content), save=False)
        report.status = 'done'
        report.save(update_fields=['file', 'status', 'updated_at'])

        Notification.objects.create(
            user=report.requested_by,
            title='Relatório pronto',
            message=f'Seu relatório {report.format.upper()} foi gerado.',
            level='success',
            link=f'/reports/{report.pk}/',
        )
    except Exception as exc:
        report.status = 'failed'
        report.error = str(exc)
        report.save(update_fields=['status', 'error', 'updated_at'])
        raise self.retry(exc=exc)
