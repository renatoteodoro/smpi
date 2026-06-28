# Arquitetura

> Esta página é um resumo. Para detalhes completos, veja [architecture/overview.md](architecture/overview.md).

## Stack

| Camada | Tecnologia |
|---|---|
| Web / API | Python 3.13 · Django 6.0 · Django REST Framework |
| Orquestração de IA | LangChain · LangGraph (`StateGraph` 9 nós) |
| LLM | gpt-4o-mini (OpenAI) — configurável via `LLM_MODEL` |
| Embeddings | sentence-transformers `paraphrase-multilingual-MiniLM-L12-v2` (local) |
| Banco de dados | PostgreSQL 16 + pgvector (vetores 18-dim e 384-dim) |
| Tarefas assíncronas | Celery + RabbitMQ (broker) + Redis (backend/cache) |
| WhatsApp | Evolution API v2 |
| Infra | Docker Swarm · Traefik (TLS wildcard via DNS-01/Cloudflare) |

## Apps Django

| App | Responsabilidade |
|---|---|
| `core` | Projeto Django, settings, URLs raiz, `/health/` |
| `base` | `TimeStampedModel`, mixins de permissão, middleware de media |
| `accounts` | Custom User (login por email), papéis admin/maintenance/viewer |
| `assets` | CRUD de `Equipment` e `MeasurementPoint` |
| `monitoring` | `SensorReading` (166k registros), ingestão REST/CSV/manual |
| `faults` | Catálogo `Fault` com `is_problem` (estado vs problema) |
| `knowledge` | `KnowledgeDocument`, `DocumentChunk`, ingestão RAG + OCR |
| `prescriptions` | `Prescription`, pipeline LangGraph 9 nós |
| `analytics` | Dashboard KPIs + Chart.js |
| `reports` | Exportação PDF/CSV |
| `ai` | Agente LangGraph, 8 ferramentas, chat SSE, chatbot flutuante |
| `notifications` | Notificações in-app |
| `whatsapp` | Webhook + envio via Evolution API v2 |
| `api` | DRF + drf-spectacular (Swagger `/api/docs/`) |

## Modelo de dados

```
Equipment ──< MeasurementPoint ──< SensorReading >── Fault
                                        │
                                    Prescription ──< DocumentChunk
                                                          │
                                                   KnowledgeDocument

User ──< ChatSession ──< ChatMessage
User ──< Notification
WhatsAppMessage (log in/out)
```

## Pipeline de IA

```
Novo evento
    ↓
preprocess — padroniza unidades (mm/s, °C), extrai 18 features, normaliza StandardScaler
    ↓
classify — estado (normal/baseline/…) → encerra | problema → continua
    ↓
similarity — ANN L2Distance pgvector k=15
    ↓
identify_fault — voto ponderado por 1/distância
    ↓
metrics — conta ocorrências e frequência
    ↓
check_docs — há DocumentChunks para o defeito?
    ├── Sim → rag (CosineDistance top-5) → generate (gpt-4o-mini grounded)
    └── Não → guard (reporta não documentado, is_grounded=False)
```

## Redes Docker (produção)

| Rede | Tipo | Serviços |
|---|---|---|
| `traefik_public` | external, com internet | traefik, app |
| `smpi_v1_internal` | internal, sem internet | app, postgresql, redis, rabbitmq, evolution_redis, evolution_api, celery_worker, celery_beat |
| `smpi_v1_egress` | overlay, com internet, sem Traefik | evolution_api, celery_worker, celery_beat |

> `celery_worker`, `celery_beat` e `evolution_api` **nunca** entram em `traefik_public`.
