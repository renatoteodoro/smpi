# Arquitetura

## Stack

| Camada | Tecnologia |
|---|---|
| Web / API | Python 3.13 · Django 6.0 · Django REST Framework |
| Orquestração de IA | LangChain · LangGraph |
| Banco de dados | PostgreSQL + pgvector |
| Tarefas assíncronas | Celery + RabbitMQ (broker) + Redis (backend/cache) |
| LLM | GPT-5.5-mini (OpenAI) — provider configurável no `.env` |
| Embeddings | sentence-transformers (local) |
| WhatsApp | Evolution API |
| Infra | Docker Swarm · Traefik (TLS wildcard via DNS-01/Cloudflare) |

## Apps Django planejados

| App | Responsabilidade |
|---|---|
| `core` | Projeto Django, settings, URLs raiz, `/health/` |
| `base` | `TimeStampedModel`, mixins de permissão, middleware de media |
| `accounts` | Custom User (login por email), papéis, recuperação de senha |
| `assets` | CRUD de `Equipment` e `MeasurementPoint` |
| `monitoring` | Ingestão de eventos, listagem, detalhe |
| `faults` | Catálogo de `Fault` com `is_problem` |
| `knowledge` | Upload de documentos, chunking, embedding (RAG) |
| `prescriptions` | Geração e persistência de recomendações prescritivas |
| `analytics` | Dashboards e gráficos |
| `reports` | Exportação PDF e CSV |
| `ai` | Grafo LangGraph, tools, sessões de chat (SSE stream) |
| `notifications` | Notificações in-app |
| `whatsapp` | Webhook e envio via Evolution API |
| `api` | DRF + drf-spectacular (Swagger/OpenAPI) |

## Modelo de dados (planejado)

```
Equipment ──< MeasurementPoint ──< SensorReading >── Fault
                                        │
                                    Prescription ──< DocumentChunk
                                                          │
                                                   KnowledgeDocument

User ──< ChatSession ──< ChatMessage
User ──< Notification
```

Entidades principais:

- **Equipment** — ativo industrial (motor, bomba, etc.)
- **MeasurementPoint** — ponto de sensor no equipamento (eixo X/Z)
- **Fault** — catálogo de defeitos/estados; campo `is_problem` distingue estado de problema
- **SensorReading** — evento de sensor; armazena métricas brutas (JSONB) e `feature_vector` (pgvector)
- **KnowledgeDocument / DocumentChunk** — base documental para RAG; chunks com embedding pgvector
- **Prescription** — recomendação gerada; vincula `SensorReading`, `Fault` e `DocumentChunk` fonte
- **ChatSession / ChatMessage** — histórico de chat por usuário

## Pipeline de IA

```
Novo evento
    ↓
Pré-processar (padronizar unidades mm/s e °C, normalizar com StandardScaler)
    ↓
Classificar: Estado ou Problema?
    ├── Estado (normal/baseline/teste/acelerando/motor_desligado) → encerrar
    └── Problema → continuar
          ↓
    Busca por similaridade (pgvector K-NN)
          ↓
    Identificar tipo de defeito (votação ponderada por similaridade)
          ↓
    Existe documentação para o defeito?
          ├── Sim → RAG → gerar prescrição grounded (GPT-5.5-mini + fontes)
          └── Não → regra de guarda: reportar sem documentação + sugerir registro
```

## Redes Docker (produção)

| Rede | Tipo | Serviços |
|---|---|---|
| `traefik_public` | external, com internet | traefik, app |
| `smpi_v1_internal` | internal, sem internet | app, postgresql, redis, rabbitmq, evolution_redis, evolution_api, celery_worker, celery_beat |
| `smpi_v1_egress` | overlay, com internet, sem Traefik | evolution_api, celery_worker, celery_beat |

> `celery_worker`, `celery_beat` e `evolution_api` **nunca** entram em `traefik_public`.
