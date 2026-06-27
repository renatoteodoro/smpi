"""
ANN similarity search and fault voting utilities.

Uses pgvector L2Distance for approximate nearest-neighbour lookup
on labelled problem readings.
"""

from collections import defaultdict

import numpy as np
from pgvector.django import L2Distance

from .models import SensorReading


def find_similar_readings(feature_vector: list, k: int = 10, exclude_id: int = None):
    """Return K nearest SensorReadings labelled as problems, ordered by L2 distance."""
    vec = np.array(feature_vector, dtype=float)
    qs = SensorReading.objects.filter(
        status_class='problem',
        feature_vector__isnull=False,
    ).select_related('fault', 'measurement_point__equipment')

    if exclude_id:
        qs = qs.exclude(id=exclude_id)

    return list(
        qs.annotate(distance=L2Distance('feature_vector', vec)).order_by('distance')[:k]
    )


def identify_fault_by_voting(similar_readings) -> int | None:
    """Weighted vote by 1/distance; returns Fault pk of winner or None."""
    votes: dict[int, float] = defaultdict(float)
    for r in similar_readings:
        if r.fault_id is not None:
            dist = getattr(r, 'distance', None) or 1.0
            weight = 1.0 / max(dist, 1e-9)
            votes[r.fault_id] += weight
    if not votes:
        return None
    return max(votes, key=votes.get)


def compute_occurrence_metrics(similar_readings, fault_id: int) -> dict:
    """Compute count and frequency description for a fault among similar readings."""
    matching = [r for r in similar_readings if r.fault_id == fault_id]
    count = len(matching)
    if count == 0:
        return {'count': 0, 'frequency': 'Nenhuma ocorrência similar encontrada.'}

    dates = [r.event_created_at for r in matching if r.event_created_at]
    if len(dates) >= 2:
        dates_sorted = sorted(dates)
        span = (dates_sorted[-1] - dates_sorted[0]).days or 1
        freq = f'{count} ocorrências em {span} dias (≈{count / span * 30:.1f}/mês)'
    else:
        freq = f'{count} ocorrência(s) identificada(s)'

    return {'count': count, 'frequency': freq}
