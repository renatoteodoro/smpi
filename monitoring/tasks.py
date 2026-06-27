from celery import shared_task


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def analyse_reading(self, reading_id: int):
    """Trigger the prescription pipeline for a SensorReading.

    The view dispatches this task and returns immediately. The pipeline
    itself runs in prescriptions.tasks.run_prescription_pipeline.
    """
    try:
        from prescriptions.tasks import run_prescription_pipeline
        run_prescription_pipeline.delay(reading_id)
    except Exception as exc:
        raise self.retry(exc=exc)
