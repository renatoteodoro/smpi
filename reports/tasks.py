from celery import shared_task


def _build_queryset(report):
    from monitoring.models import SensorReading
    qs = SensorReading.objects.all()
    if report.filters.get('status'):
        qs = qs.filter(status_class=report.filters['status'])
    if report.filters.get('fault'):
        qs = qs.filter(fault__code=report.filters['fault'])
    if report.filters.get('date_from'):
        qs = qs.filter(event_created_at__date__gte=report.filters['date_from'])
    if report.filters.get('date_to'):
        qs = qs.filter(event_created_at__date__lte=report.filters['date_to'])
    return qs


def _run_generation(report):
    """Core generation logic — no Celery dependency, safe to call directly."""
    from django.core.files.base import ContentFile
    from notifications.models import Notification

    report.status = 'processing'
    report.save(update_fields=['status', 'updated_at'])

    try:
        qs = _build_queryset(report)

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
            message=f'Seu relatório {report.format.upper()} está disponível para download.',
            level='success',
            link=f'/reports/{report.pk}/download/',
        )
    except Exception as exc:
        report.status = 'failed'
        report.error = str(exc)
        report.save(update_fields=['status', 'error', 'updated_at'])
        raise


@shared_task(bind=True, max_retries=1, default_retry_delay=60)
def generate_report(self, report_id: int):
    from .models import ReportRequest
    report = ReportRequest.objects.get(pk=report_id)
    try:
        _run_generation(report)
    except Exception as exc:
        try:
            self.retry(exc=exc)
        except Exception:
            pass
