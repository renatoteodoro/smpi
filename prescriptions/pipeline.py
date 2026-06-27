import logging

logger = logging.getLogger(__name__)


def execute_pipeline(reading):
    """Run the full LangGraph pipeline and persist the Prescription. Idempotent."""
    from faults.models import Fault
    from knowledge.models import DocumentChunk
    from .graph import build_graph
    from .models import Prescription

    initial = {
        'reading_id': reading.pk,
        'metrics': reading.metrics or {},
        'feature_vector': [],
        'status_class': 'pending',
        'similar_readings': [],
        'fault_id': reading.fault_id,
        'fault_code': reading.fault.code if reading.fault else None,
        'fault_name': reading.fault.name if reading.fault else None,
        'occurrences_count': 0,
        'occurrences_frequency': '',
        'chunks': [],
        'has_documentation': False,
        'instructions': '',
        'source_chunk_ids': [],
        'is_grounded': True,
        'error': None,
    }

    try:
        result = build_graph().invoke(initial)
    except Exception as e:
        logger.error(f'Pipeline failed for reading {reading.pk}: {e}')
        result = {**initial, 'instructions': f'Erro no pipeline: {e}', 'is_grounded': False, 'error': str(e)}

    fault = Fault.objects.filter(pk=result.get('fault_id')).first() if result.get('fault_id') else None

    p, _ = Prescription.objects.update_or_create(
        sensor_reading=reading,
        defaults={
            'fault': fault,
            'defect_type': result.get('fault_name') or result.get('fault_code') or '',
            'occurrences_count': result.get('occurrences_count', 0),
            'occurrences_frequency': result.get('occurrences_frequency', ''),
            'instructions': result.get('instructions', ''),
            'is_grounded': result.get('is_grounded', True),
            'pipeline_log': {
                'status_class': result.get('status_class'),
                'has_documentation': result.get('has_documentation'),
                'similar_count': len(result.get('similar_readings', [])),
                'chunks_used': len(result.get('source_chunk_ids', [])),
                'error': result.get('error'),
            },
        }
    )

    chunk_ids = result.get('source_chunk_ids', [])
    if chunk_ids:
        p.source_chunks.set(DocumentChunk.objects.filter(pk__in=chunk_ids))

    new_status = result.get('status_class', '')
    if new_status in ('state', 'problem') and new_status != reading.status_class:
        update_fields = ['status_class', 'updated_at']
        reading.status_class = new_status
        if fault and reading.fault is None:
            reading.fault = fault
            update_fields.append('fault')
        reading.save(update_fields=update_fields)

    return p
