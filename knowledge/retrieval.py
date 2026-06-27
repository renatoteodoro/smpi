from pgvector.django import CosineDistance

from .models import DocumentChunk
from .ingest import embed_texts


def embed_query(query: str) -> list:
    """Embed a single query string."""
    results = embed_texts([query])
    return results[0] if results else []


def retrieve_chunks(query_embedding: list, fault_id: int = None, k: int = 5) -> list:
    """
    Retrieve top-k DocumentChunks by cosine similarity.
    Scope: fault-specific first; if none found, fall back to global corpus.
    """
    base_qs = DocumentChunk.objects.filter(embedding__isnull=False).select_related('document__fault')

    if fault_id:
        scoped = list(
            base_qs.filter(document__fault_id=fault_id)
            .annotate(score=CosineDistance('embedding', query_embedding))
            .order_by('score')[:k]
        )
        if scoped:
            return scoped
        # Fall back to global corpus (documents with no fault restriction)

    return list(
        base_qs.annotate(score=CosineDistance('embedding', query_embedding))
        .order_by('score')[:k]
    )


def has_documentation_for_fault(fault_id: int) -> bool:
    """
    True if there are indexed chunks for this fault OR any global chunks.
    Global documents (fault=None) serve as a universal knowledge base.
    """
    # Fault-specific docs take priority
    if DocumentChunk.objects.filter(
        document__fault_id=fault_id,
        embedding__isnull=False,
    ).exists():
        return True
    # Fall back: any indexed chunk at all acts as global knowledge base
    return DocumentChunk.objects.filter(embedding__isnull=False).exists()
