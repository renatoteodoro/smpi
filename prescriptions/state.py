from typing import Any, List, Optional, TypedDict


class PrescriptionState(TypedDict):
    reading_id: int
    metrics: dict
    feature_vector: List[float]
    status_class: str
    similar_readings: List[Any]
    fault_id: Optional[int]
    fault_code: Optional[str]
    fault_name: Optional[str]
    occurrences_count: int
    occurrences_frequency: str
    chunks: List[Any]
    has_documentation: bool
    instructions: str
    source_chunk_ids: List[int]
    is_grounded: bool
    error: Optional[str]
