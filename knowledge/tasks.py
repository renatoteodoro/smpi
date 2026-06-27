from celery import shared_task


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def ingest_document_task(self, document_id: int):
    """Async document ingestion: extract → chunk → embed → store."""
    try:
        from accounts.models import User
        from notifications.models import Notification

        from .ingest import ingest_document
        from .models import KnowledgeDocument

        doc = KnowledgeDocument.objects.get(pk=document_id)
        count = ingest_document(doc)

        for user in User.objects.filter(role__in=['admin', 'maintenance'], is_active=True):
            Notification.objects.create(
                user=user,
                title='Documento indexado',
                message=f'"{doc.title}" foi indexado com {count} chunks.',
                level='success',
                link=f'/knowledge/{doc.pk}/',
            )
    except Exception as exc:
        raise self.retry(exc=exc)
