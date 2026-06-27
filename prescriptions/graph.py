from langgraph.graph import END, StateGraph

from .nodes import (
    check_docs_node,
    classify_node,
    generate_node,
    guard_node,
    identify_fault_node,
    metrics_node,
    preprocess_node,
    rag_node,
    similarity_node,
)
from .state import PrescriptionState


def _route_classify(state: dict) -> str:
    return 'end_state' if state.get('status_class') == 'state' else 'similarity'


def _route_check_docs(state: dict) -> str:
    return 'rag' if state.get('has_documentation') else 'guard'


def build_graph():
    g = StateGraph(PrescriptionState)

    g.add_node('preprocess', preprocess_node)
    g.add_node('classify', classify_node)
    g.add_node('similarity', similarity_node)
    g.add_node('identify_fault', identify_fault_node)
    g.add_node('metrics', metrics_node)
    g.add_node('check_docs', check_docs_node)
    g.add_node('rag', rag_node)
    g.add_node('generate', generate_node)
    g.add_node('guard', guard_node)

    g.set_entry_point('preprocess')
    g.add_edge('preprocess', 'classify')
    g.add_conditional_edges('classify', _route_classify, {'end_state': END, 'similarity': 'similarity'})
    g.add_edge('similarity', 'identify_fault')
    g.add_edge('identify_fault', 'metrics')
    g.add_edge('metrics', 'check_docs')
    g.add_conditional_edges('check_docs', _route_check_docs, {'rag': 'rag', 'guard': 'guard'})
    g.add_edge('rag', 'generate')
    g.add_edge('generate', END)
    g.add_edge('guard', END)

    return g.compile()
