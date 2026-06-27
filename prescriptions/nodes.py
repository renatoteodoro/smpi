import logging

logger = logging.getLogger(__name__)


def preprocess_node(state: dict) -> dict:
    try:
        from monitoring.preprocessing import extract_features, normalize_features
        raw = extract_features(state.get('metrics', {}))
        return {'feature_vector': normalize_features(raw)}
    except Exception as e:
        logger.error(f'preprocess_node: {e}')
        return {'feature_vector': [], 'error': str(e)}


def classify_node(state: dict) -> dict:
    from monitoring.models import SensorReading
    try:
        reading = SensorReading.objects.select_related('fault').get(pk=state['reading_id'])
        if reading.fault:
            status = 'problem' if reading.fault.is_problem else 'state'
            return {
                'status_class': status,
                'fault_id': reading.fault.pk if reading.fault.is_problem else None,
                'fault_code': reading.fault.code if reading.fault.is_problem else None,
                'fault_name': reading.fault.name if reading.fault.is_problem else None,
            }
        return {'status_class': 'problem'}
    except Exception as e:
        logger.error(f'classify_node: {e}')
        return {'status_class': 'problem', 'error': str(e)}


def similarity_node(state: dict) -> dict:
    from monitoring.similarity import find_similar_readings
    try:
        similar = find_similar_readings(
            feature_vector=state.get('feature_vector', []),
            k=15,
            exclude_id=state['reading_id'],
        )
        return {'similar_readings': similar}
    except Exception as e:
        logger.error(f'similarity_node: {e}')
        return {'similar_readings': [], 'error': str(e)}


def identify_fault_node(state: dict) -> dict:
    from monitoring.similarity import identify_fault_by_voting
    from faults.models import Fault
    similar = state.get('similar_readings', [])
    if not similar:
        return {}
    fault_pk = identify_fault_by_voting(similar)
    if fault_pk is None:
        return {}
    try:
        fault = Fault.objects.get(pk=fault_pk)
        return {'fault_id': fault.pk, 'fault_code': fault.code, 'fault_name': fault.name}
    except Fault.DoesNotExist:
        return {}


def metrics_node(state: dict) -> dict:
    from monitoring.similarity import compute_occurrence_metrics
    similar = state.get('similar_readings', [])
    fault_id = state.get('fault_id')
    if not fault_id or not similar:
        return {'occurrences_count': 0, 'occurrences_frequency': 'Nenhuma ocorrência similar.'}
    result = compute_occurrence_metrics(similar, fault_id)
    return {'occurrences_count': result['count'], 'occurrences_frequency': result['frequency']}


def check_docs_node(state: dict) -> dict:
    fault_id = state.get('fault_id')
    if not fault_id:
        return {'has_documentation': False}
    try:
        from knowledge.retrieval import has_documentation_for_fault
        return {'has_documentation': has_documentation_for_fault(fault_id)}
    except Exception as e:
        logger.error(f'check_docs_node: {e}')
        return {'has_documentation': False}


def rag_node(state: dict) -> dict:
    fault_name = state.get('fault_name') or state.get('fault_code', '')
    try:
        from knowledge.retrieval import retrieve_chunks, embed_query
        query_emb = embed_query(f'Manutenção e solução para defeito: {fault_name}')
        chunks = retrieve_chunks(query_emb, fault_id=state.get('fault_id'), k=5)
        return {'chunks': chunks}
    except Exception as e:
        logger.error(f'rag_node: {e}')
        return {'chunks': [], 'error': str(e)}


def generate_node(state: dict) -> dict:
    from langchain_core.messages import HumanMessage, SystemMessage
    from .llm import get_llm

    chunks = state.get('chunks', [])
    if not chunks:
        return guard_node(state)

    fault_code = state.get('fault_code', '')
    fault_name = state.get('fault_name', fault_code)
    occurrences = state.get('occurrences_count', 0)
    frequency = state.get('occurrences_frequency', '')

    context_text = '\n\n---\n\n'.join([
        f'[Documento: {c.document.title}, Trecho {c.chunk_index}]\n{c.content}'
        for c in chunks
    ])

    system_prompt = (
        'Você é um especialista em manutenção industrial e vai orientar um técnico de campo.\n'
        'Escreva em linguagem clara, direta e acessível — sem jargão técnico desnecessário.\n'
        'Use frases curtas. O técnico precisa entender rapidamente o que fazer.\n'
        'Baseie-se APENAS nos documentos fornecidos. Nunca invente procedimentos.\n'
        'Formate a resposta em Markdown simples (títulos, listas numeradas, negrito).'
    )

    user_prompt = (
        f'Um técnico precisa de orientação sobre o seguinte defeito detectado:\n\n'
        f'**Defeito:** {fault_name}\n'
        f'**Ocorrências similares encontradas:** {occurrences}\n'
        f'**Frequência de ocorrência:** {frequency}\n\n'
        f'---\n\n'
        f'**Documentação técnica disponível:**\n\n{context_text}\n\n'
        f'---\n\n'
        f'Com base nos documentos acima, escreva uma orientação para o técnico com:\n\n'
        f'1. **O que está acontecendo** — explique o defeito em linguagem simples\n'
        f'2. **Por que acontece** — causas mais prováveis\n'
        f'3. **O que fazer agora** — passos práticos de inspeção e correção, em ordem\n'
        f'4. **Como evitar que volte a acontecer** — ações preventivas\n\n'
        f'Ao final, mencione quais documentos foram usados como referência.'
    )

    try:
        llm = get_llm()
        response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)])
        instructions = response.content if hasattr(response, 'content') else str(response)
        return {
            'instructions': instructions,
            'source_chunk_ids': [c.pk for c in chunks],
            'is_grounded': True,
        }
    except Exception as e:
        logger.error(f'generate_node LLM error: {e}')
        fallback = '\n\n'.join([f'**{c.document.title}**\n{c.content}' for c in chunks])
        return {
            'instructions': fallback,
            'source_chunk_ids': [c.pk for c in chunks],
            'is_grounded': True,
        }


def guard_node(state: dict) -> dict:
    fault_code = state.get('fault_code', 'desconhecido')
    return {
        'instructions': (
            f'## Defeito não documentado\n\n'
            f'O defeito **`{fault_code}`** não possui documentação orientativa.\n\n'
            f'**Ação:** Registre um documento orientativo em '
            f'_Base de Conhecimento → Novo Documento_.\n\n'
            f'_Nenhuma instrução foi gerada para evitar recomendações sem base documental._'
        ),
        'source_chunk_ids': [],
        'is_grounded': False,
    }
