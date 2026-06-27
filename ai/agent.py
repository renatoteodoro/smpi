import logging

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import tool

logger = logging.getLogger(__name__)

_RECUSA_FORA_ESCOPO = (
    'Só posso responder sobre o sistema SMPI — equipamentos, eventos, defeitos, '
    'prescrições e documentação técnica. Como posso ajudar com isso?'
)

SYSTEM_PROMPT = (
    'Você é um assistente técnico do sistema SMPI (Sistema de Manutenção Prescritiva Industrial).\n\n'

    '=== RESTRIÇÃO DE ESCOPO — PRIORIDADE MÁXIMA ===\n\n'

    'Você responde EXCLUSIVAMENTE perguntas diretamente relacionadas ao sistema SMPI. '
    'Temas permitidos:\n'
    '  - Equipamentos industriais e pontos de medição cadastrados no sistema\n'
    '  - Eventos de sensor (leituras de vibração, temperatura, RPM, aceleração)\n'
    '  - Defeitos e falhas industriais identificados pelo SMPI\n'
    '  - Prescrições de manutenção geradas pela IA do sistema\n'
    '  - Documentação técnica da base de conhecimento do SMPI\n\n'

    'QUALQUER outro assunto — receitas, culinária, entretenimento, esportes, política, '
    'história geral, ciência geral, clima, piadas, matemática geral, relacionamentos '
    'ou qualquer tema não listado acima — deve receber EXATAMENTE esta resposta, '
    'sem acrescentar nem remover nada:\n\n'

    f'    "{_RECUSA_FORA_ESCOPO}"\n\n'

    'Não justifique a recusa. Não peça desculpas elaboradas. '
    'Não ofereça alternativas. Use SOMENTE essa frase para perguntas fora do escopo.\n\n'

    '=== INSTRUÇÕES PARA PERGUNTAS DENTRO DO ESCOPO ===\n\n'

    '1. SEMPRE chame uma ferramenta antes de responder com qualquer dado do sistema. '
    'Nunca afirme valores, quantidades ou nomes que não vieram de uma ferramenta.\n'
    '2. Se tiver dúvida se uma pergunta está dentro do escopo, chame verificar_escopo '
    'antes de qualquer outra ação.\n'
    '3. Responda em português, com linguagem clara e acessível para técnicos de campo.\n'
    '4. Formate respostas em Markdown (títulos, negrito, listas).\n'
    '5. Em listas longas, agrupe e resuma — não exiba listas brutas.\n'
    '6. Nunca invente defeitos, prescrições ou procedimentos que não existem no sistema.'
)


# ── Equipamentos ──────────────────────────────────────────────────────────────

@tool
def listar_equipamentos() -> str:
    """Lista todos os equipamentos cadastrados com seu status e contagem de eventos."""
    from assets.models import Equipment
    from monitoring.models import SensorReading
    items = Equipment.objects.all().order_by('name')
    if not items.exists():
        return 'Nenhum equipamento cadastrado.'
    lines = []
    for e in items:
        total = SensorReading.objects.filter(measurement_point__equipment=e).count()
        problems = SensorReading.objects.filter(measurement_point__equipment=e, status_class='problem').count()
        lines.append(
            f'- **{e.name}** ({e.equipment_type}, {e.sector}) — Status: {e.get_status_display()} | '
            f'{total} eventos, {problems} problemas'
        )
    return '\n'.join(lines)


@tool
def detalhar_equipamento(nome_ou_id: str) -> str:
    """
    Retorna detalhes completos de um equipamento: pontos de medição,
    contagem de defeitos por tipo e os 5 eventos mais recentes.
    Aceita nome parcial ou ID numérico.
    """
    from assets.models import Equipment
    from monitoring.models import SensorReading
    from django.db.models import Count

    try:
        if nome_ou_id.isdigit():
            eq = Equipment.objects.get(pk=int(nome_ou_id))
        else:
            eq = Equipment.objects.filter(name__icontains=nome_ou_id).first()
        if not eq:
            return f'Equipamento "{nome_ou_id}" não encontrado.'
    except Equipment.DoesNotExist:
        return f'Equipamento "{nome_ou_id}" não encontrado.'

    points = eq.measurement_points.all()
    points_str = ', '.join(p.name for p in points) or 'Nenhum'

    # Top defeitos
    top_faults = (
        SensorReading.objects.filter(measurement_point__equipment=eq, status_class='problem', fault__isnull=False)
        .values('fault__code', 'fault__name')
        .annotate(total=Count('id'))
        .order_by('-total')[:5]
    )
    faults_str = '\n'.join(
        f'  - {f["fault__name"]} (`{f["fault__code"]}`): {f["total"]} ocorrências'
        for f in top_faults
    ) or '  Nenhum defeito registrado.'

    # Últimos 5 eventos
    recent = SensorReading.objects.filter(
        measurement_point__equipment=eq
    ).select_related('fault').order_by('-event_created_at')[:5]
    recent_str = '\n'.join(
        f'  - #{r.external_id or r.pk} em {r.event_created_at.strftime("%d/%m/%Y %H:%M") if r.event_created_at else "?"} '
        f'— {r.fault.name if r.fault else "sem defeito"} ({r.status_class})'
        for r in recent
    ) or '  Sem eventos recentes.'

    return (
        f'**{eq.name}**\n'
        f'Tipo: {eq.equipment_type} | Setor: {eq.sector} | Status: {eq.get_status_display()}\n'
        f'Pontos de medição: {points_str}\n\n'
        f'**Top 5 defeitos:**\n{faults_str}\n\n'
        f'**Últimos 5 eventos:**\n{recent_str}'
    )


# ── Eventos / Leituras ────────────────────────────────────────────────────────

@tool
def listar_eventos(
    equipamento: str = '',
    status: str = '',
    defeito: str = '',
    data_inicio: str = '',
    data_fim: str = '',
    limite: int = 10,
) -> str:
    """
    Lista eventos de sensor com filtros opcionais.
    - equipamento: nome parcial ou ID do equipamento
    - status: 'problem', 'state' ou 'pending'
    - defeito: código ou nome parcial do defeito
    - data_inicio / data_fim: formato DD/MM/AAAA
    - limite: máximo de registros (padrão 10, máximo 50)
    """
    from monitoring.models import SensorReading
    from django.utils.dateparse import parse_date
    from datetime import datetime

    qs = SensorReading.objects.select_related('fault', 'measurement_point__equipment').order_by('-event_created_at')

    if equipamento:
        if equipamento.isdigit():
            qs = qs.filter(measurement_point__equipment_id=int(equipamento))
        else:
            qs = qs.filter(measurement_point__equipment__name__icontains=equipamento)

    if status:
        qs = qs.filter(status_class=status)

    if defeito:
        qs = qs.filter(fault__code__icontains=defeito) | qs.filter(fault__name__icontains=defeito)

    if data_inicio:
        try:
            d = datetime.strptime(data_inicio, '%d/%m/%Y').date()
            qs = qs.filter(event_created_at__date__gte=d)
        except ValueError:
            pass

    if data_fim:
        try:
            d = datetime.strptime(data_fim, '%d/%m/%Y').date()
            qs = qs.filter(event_created_at__date__lte=d)
        except ValueError:
            pass

    limite = min(int(limite), 50)
    total = qs.count()
    eventos = qs[:limite]

    if not eventos:
        return 'Nenhum evento encontrado com os filtros informados.'

    lines = [f'Exibindo {min(limite, total)} de {total} eventos:\n']
    for r in eventos:
        data = r.event_created_at.strftime('%d/%m/%Y %H:%M') if r.event_created_at else '?'
        eq_name = r.measurement_point.equipment.name if r.measurement_point else '?'
        defeito_str = r.fault.name if r.fault else 'sem defeito'
        lines.append(
            f'- **#{r.external_id or r.pk}** | {data} | {eq_name} | '
            f'{defeito_str} | status: {r.status_class}'
        )
    return '\n'.join(lines)


@tool
def detalhar_evento(reading_id: int) -> str:
    """
    Retorna todos os detalhes de um evento de sensor (leitura), incluindo
    métricas, defeito identificado e prescrição completa se disponível.
    """
    from monitoring.models import SensorReading
    try:
        r = SensorReading.objects.select_related('fault', 'measurement_point__equipment').get(pk=reading_id)
    except SensorReading.DoesNotExist:
        return f'Evento #{reading_id} não encontrado.'

    data = r.event_created_at.strftime('%d/%m/%Y %H:%M') if r.event_created_at else '?'
    eq = r.measurement_point.equipment.name if r.measurement_point else '?'

    result = (
        f'**Evento #{r.external_id or r.pk}**\n'
        f'Equipamento: {eq}\n'
        f'Data: {data}\n'
        f'Defeito: {r.fault.name if r.fault else "não identificado"} '
        f'(`{r.fault.code if r.fault else "-"}`)\n'
        f'Status: {r.status_class}\n'
        f'RPM: {r.rpm or "—"}\n'
    )

    try:
        p = r.prescription
        result += (
            f'\n**Prescrição:**\n'
            f'Tipo de defeito: {p.defect_type}\n'
            f'Ocorrências similares: {p.occurrences_count}\n'
            f'Fundamentada em documentação: {"Sim" if p.is_grounded else "Não"}\n\n'
            f'**Instruções:**\n{p.instructions[:1000]}'
            + ('...' if len(p.instructions) > 1000 else '')
        )
    except Exception:
        result += '\nSem prescrição disponível para este evento.'

    return result


# ── Prescrições ───────────────────────────────────────────────────────────────

@tool
def listar_prescricoes(
    equipamento: str = '',
    fundamentada: str = '',
    limite: int = 10,
) -> str:
    """
    Lista prescrições geradas pelo sistema.
    - equipamento: nome parcial ou ID
    - fundamentada: 'sim' para prescrições com base documental, 'nao' para as sem documentação
    - limite: máximo de registros (padrão 10)
    """
    from prescriptions.models import Prescription
    from django.db.models import Q

    qs = Prescription.objects.select_related(
        'fault', 'sensor_reading__measurement_point__equipment'
    ).order_by('-updated_at')

    if equipamento:
        if equipamento.isdigit():
            qs = qs.filter(sensor_reading__measurement_point__equipment_id=int(equipamento))
        else:
            qs = qs.filter(sensor_reading__measurement_point__equipment__name__icontains=equipamento)

    if fundamentada.lower() in ('sim', 'yes', 'true', '1'):
        qs = qs.filter(is_grounded=True)
    elif fundamentada.lower() in ('nao', 'não', 'no', 'false', '0'):
        qs = qs.filter(is_grounded=False)

    total = qs.count()
    limite = min(int(limite), 50)
    items = qs[:limite]

    if not items:
        return 'Nenhuma prescrição encontrada.'

    lines = [f'Exibindo {min(limite, total)} de {total} prescrições:\n']
    for p in items:
        eq = p.sensor_reading.measurement_point.equipment.name if p.sensor_reading.measurement_point else '?'
        data = p.updated_at.strftime('%d/%m/%Y') if p.updated_at else '?'
        grounded = '✓ documentada' if p.is_grounded else '⚠ sem documentação'
        lines.append(
            f'- **{p.defect_type or "Defeito desconhecido"}** | {eq} | {data} | '
            f'{p.occurrences_count} ocorrências | {grounded}'
        )
    return '\n'.join(lines)


# ── Defeitos ──────────────────────────────────────────────────────────────────

@tool
def resumo_defeitos(equipamento: str = '', top: int = 10) -> str:
    """
    Mostra os defeitos mais frequentes no sistema ou em um equipamento específico.
    - equipamento: nome parcial ou ID (opcional, se vazio mostra geral)
    - top: quantos defeitos mostrar (padrão 10)
    """
    from monitoring.models import SensorReading
    from django.db.models import Count

    qs = SensorReading.objects.filter(status_class='problem', fault__isnull=False)
    if equipamento:
        if equipamento.isdigit():
            qs = qs.filter(measurement_point__equipment_id=int(equipamento))
        else:
            qs = qs.filter(measurement_point__equipment__name__icontains=equipamento)

    top_faults = (
        qs.values('fault__code', 'fault__name')
        .annotate(total=Count('id'))
        .order_by('-total')[:int(top)]
    )

    if not top_faults:
        return 'Nenhum defeito registrado com os filtros informados.'

    total_geral = qs.count()
    escopo = f'em "{equipamento}"' if equipamento else 'no sistema'
    lines = [f'**Top {top} defeitos {escopo}** (total: {total_geral} ocorrências de problema):\n']
    for i, f in enumerate(top_faults, 1):
        pct = round(f['total'] / total_geral * 100, 1) if total_geral else 0
        lines.append(f'{i}. **{f["fault__name"]}** (`{f["fault__code"]}`): {f["total"]} ocorrências ({pct}%)')
    return '\n'.join(lines)


@tool
def estatisticas_sistema() -> str:
    """
    Retorna um resumo geral do sistema: total de equipamentos, eventos,
    prescrições, defeitos únicos e distribuição por status.
    """
    from assets.models import Equipment
    from monitoring.models import SensorReading
    from faults.models import Fault
    from prescriptions.models import Prescription

    total_eq = Equipment.objects.count()
    total_events = SensorReading.objects.count()
    problems = SensorReading.objects.filter(status_class='problem').count()
    states = SensorReading.objects.filter(status_class='state').count()
    pending = SensorReading.objects.filter(status_class='pending').count()
    total_faults = Fault.objects.filter(is_problem=True).count()
    total_presc = Prescription.objects.count()
    grounded = Prescription.objects.filter(is_grounded=True).count()

    return (
        f'**Resumo do Sistema SMPI**\n\n'
        f'- Equipamentos: {total_eq}\n'
        f'- Total de eventos: {total_events:,}\n'
        f'  - Problemas: {problems:,} ({round(problems/total_events*100,1) if total_events else 0}%)\n'
        f'  - Estados operacionais: {states:,}\n'
        f'  - Pendentes: {pending:,}\n'
        f'- Tipos de defeitos cadastrados: {total_faults}\n'
        f'- Prescrições geradas: {total_presc}\n'
        f'  - Com base documental: {grounded}\n'
        f'  - Sem documentação: {total_presc - grounded}'
    )


# ── Documentação / RAG ────────────────────────────────────────────────────────

@tool
def buscar_documentacao(consulta: str, codigo_defeito: str = '') -> str:
    """
    Busca trechos relevantes na base de conhecimento técnico.
    - consulta: texto livre sobre o que procurar
    - codigo_defeito: código exato do defeito para filtrar documentos relacionados (opcional)
    """
    try:
        from knowledge.retrieval import embed_query, retrieve_chunks
        from faults.models import Fault
        fault_id = None
        if codigo_defeito:
            f = Fault.objects.filter(code=codigo_defeito).first()
            if f:
                fault_id = f.pk
        emb = embed_query(consulta)
        chunks = retrieve_chunks(emb, fault_id=fault_id, k=4)
        if not chunks:
            return 'Nenhum documento relevante encontrado.'
        return '\n\n---\n\n'.join(
            f'**[{c.document.title} — trecho {c.chunk_index}]**\n{c.content[:500]}'
            for c in chunks
        )
    except Exception as e:
        return f'Erro ao buscar documentação: {e}'


# ── Guardrail de escopo ───────────────────────────────────────────────────────

@tool
def verificar_escopo(pergunta: str) -> str:
    """
    Verifica se a pergunta está dentro do escopo do sistema SMPI.
    Use esta ferramenta quando houver dúvida se o assunto pertence ao sistema antes
    de decidir como responder. Retorna 'DENTRO' se a pergunta for sobre equipamentos,
    eventos de sensor, defeitos, prescrições ou documentação técnica do SMPI.
    Retorna 'FORA' com a instrução de recusa quando o assunto for outro qualquer.
    """
    import unicodedata

    def _normalizar(texto: str) -> str:
        """Remove acentos e converte para ASCII minúsculo para comparação robusta."""
        return (
            unicodedata.normalize('NFKD', texto)
            .encode('ascii', 'ignore')
            .decode('ascii')
            .lower()
        )

    # Palavras-chave fora de escopo (sem acentos — comparadas com pergunta normalizada)
    _OFF_TOPIC = (
        'receita', 'bolo', 'brigadeiro', 'pacoca', 'culinaria', 'cozinha',
        'comida', 'alimento', 'ingrediente', 'prato', 'comer', 'tempero',
        'filme', 'serie', 'novela', 'musica', 'cantor', 'artista', 'show',
        'futebol', 'esporte', 'jogo', 'time', 'jogador', 'campeonato',
        'politica', 'governo', 'presidente', 'eleicao', 'partido', 'voto',
        'piada', 'anedota', 'humor', 'engracado',
        'amor', 'relacionamento', 'namoro', 'casamento', 'namorado',
        'clima', 'previsao do tempo', 'chuva amanha',
        'noticia', 'jornal', 'news',
        'poema', 'poesia', 'literatura',
        'animal', 'bicho', 'cachorro', 'gato',
    )

    # Palavras-chave dentro do escopo (sem acentos)
    _IN_SCOPE = (
        'equipamento', 'motor', 'bomba', 'compressor', 'maquina', 'ativo',
        'ponto de medicao', 'sensor', 'vibracao', 'rpm',
        'aceleracao', 'kurtosis', 'rms', 'crest factor',
        'evento', 'leitura', 'medicao', 'monitoramento',
        'defeito', 'falha', 'fault', 'anomalia', 'problema industrial',
        'prescricao', 'manutencao', 'reparo', 'lubrificacao', 'instrucao tecnica',
        'documentacao tecnica', 'base de conhecimento', 'manual tecnico',
        'smpi', 'sistema de manutencao', 'manutencao prescritiva',
        'setor', 'planta industrial', 'instalacao industrial',
        'estatistica', 'frequencia de defeito', 'ocorrencia de defeito',
    )

    pergunta_norm = _normalizar(pergunta)

    for kw in _OFF_TOPIC:
        if kw in pergunta_norm:
            return (
                f'FORA — pergunta fora do escopo do SMPI (detectado: "{kw}"). '
                f'Responda exatamente com: "{_RECUSA_FORA_ESCOPO}"'
            )

    for kw in _IN_SCOPE:
        if kw in pergunta_norm:
            return (
                f'DENTRO — pergunta dentro do escopo do SMPI (detectado: "{kw}"). '
                'Prossiga usando as ferramentas disponíveis para buscar os dados reais.'
            )

    # Nenhum indicador de escopo encontrado: postura conservadora — recusar
    return (
        'FORA — a pergunta não menciona nenhum tópico do SMPI. '
        f'Responda exatamente com: "{_RECUSA_FORA_ESCOPO}"'
    )


# ── Agent setup ───────────────────────────────────────────────────────────────

_TOOLS = [
    listar_equipamentos,
    detalhar_equipamento,
    listar_eventos,
    detalhar_evento,
    listar_prescricoes,
    resumo_defeitos,
    estatisticas_sistema,
    buscar_documentacao,
    verificar_escopo,
]


def _get_agent():
    from langgraph.prebuilt import create_react_agent
    from prescriptions.llm import get_llm
    return create_react_agent(get_llm(), _TOOLS, prompt=SYSTEM_PROMPT)


def _build_history(session):
    history = []
    for msg in session.messages.all():
        if msg.role == 'user':
            history.append(HumanMessage(content=msg.content))
        elif msg.role == 'assistant':
            history.append(AIMessage(content=msg.content))
    return history


def chat_with_agent(session_id: int, user_message: str) -> str:
    from ai.models import ChatSession
    session = ChatSession.objects.prefetch_related('messages').get(pk=session_id)
    history = _build_history(session)
    history.append(HumanMessage(content=user_message))
    result = _get_agent().invoke({'messages': history})
    last = result['messages'][-1]
    return last.content if hasattr(last, 'content') else str(last)


def stream_chat_with_agent(session_id: int, user_message: str):
    """Yield string chunks from the agent stream."""
    from ai.models import ChatSession
    session = ChatSession.objects.prefetch_related('messages').get(pk=session_id)
    history = _build_history(session)
    history.append(HumanMessage(content=user_message))

    try:
        for chunk in _get_agent().stream({'messages': history}):
            if 'agent' in chunk:
                for msg in chunk['agent'].get('messages', []):
                    if hasattr(msg, 'content') and msg.content:
                        yield msg.content
    except Exception as e:
        yield f'\n\n_Erro no agente: {e}_'
