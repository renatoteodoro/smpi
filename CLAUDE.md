# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Comandos essenciais

```bash
# Ativar o ambiente virtual
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Linux/macOS

# Instalar dependências
pip install -r requirements.txt

# Migrações
python manage.py migrate
python manage.py makemigrations <app>

# Servidor de desenvolvimento
python manage.py runserver

# Criar superusuário
python manage.py createsuperuser

# Shell Django
python manage.py shell
```

Não há testes automatizados neste projeto (fora do escopo do PRD).

## Arquitetura

### Estado atual

O projeto está no **Sprint 0**. Apenas o scaffold Django (`core/`) e o design system (`design_system/`) existem. Nenhum app da aplicação foi criado ainda.

### Stack definida

| Camada | Tecnologia |
|---|---|
| Backend | Python 3.13 · Django 6.0 · Django REST Framework |
| IA | LangChain · LangGraph · sentence-transformers (embeddings locais) |
| LLM | GPT-5.5-mini via OpenAI (configurável por `LLM_PROVIDER` no `.env`) |
| Banco | PostgreSQL + pgvector |
| Tarefas async | Celery · RabbitMQ (broker) · Redis (backend + cache) |
| WhatsApp | Evolution API |
| Infra | Docker Swarm · Traefik (TLS wildcard DNS-01/Cloudflare) |

### Apps Django a serem criados (ordem dos sprints)

```
core/       — projeto (já existe), settings único, /health/
base/       — TimeStampedModel, mixins de permissão, middleware de media
accounts/   — Custom User login por email, papéis (admin/maintenance/viewer)
assets/     — Equipment, MeasurementPoint
monitoring/ — SensorReading, ingestão REST/CSV/manual
faults/     — Fault (catálogo, campo is_problem)
knowledge/  — KnowledgeDocument, DocumentChunk, ingestão RAG
prescriptions/ — Prescription, geração via Celery
analytics/  — dashboards
reports/    — exportação PDF/CSV
ai/         — grafo LangGraph, ChatSession, ChatMessage, SSE stream
notifications/ — notificações in-app
whatsapp/   — webhook + envio via Evolution API
api/        — DRF + drf-spectacular (Swagger)
```

### Regras de domínio críticas

**Estado vs Problema:** O campo `fault` de `SensorReading` pode ser um estado (`normal`, `baseline`, `teste`, `acelerando`, `motor_desligado`) ou um problema (qualquer outro valor). Estados não geram prescrição e encerram o pipeline.

**Regra de guarda (anti-alucinação):** Se não houver documentação (`KnowledgeDocument`) para o defeito identificado, o sistema **não inventa solução** — reporta que não está documentado e oferece o fluxo para registrar um novo documento. Toda recomendação deve citar as fontes.

**Tarefas pesadas são sempre assíncronas (Celery):** Análise de evento, geração de prescrição, resumos com IA e ingestão de documentos rodam em Celery. A view responde imediatamente e dispara uma notificação in-app ao concluir.

**Chat usa SSE stream:** O agente LangGraph responde token a token via `StreamingHttpResponse`. O conteúdo vem em markdown e é renderizado para HTML no template.

### Modelo de dados (planejado)

```
Equipment ──< MeasurementPoint ──< SensorReading >── Fault
                                        │
                                    Prescription ──>< DocumentChunk
                                                          │
                                                   KnowledgeDocument
```

Todos os models herdam de `TimeStampedModel` (`created_at`, `updated_at`).

### Redes Docker em produção

São exatamente **3 redes**. Nunca colocar `celery_worker`, `celery_beat` ou `evolution_api` em `traefik_public`:

| Rede | Serviços |
|---|---|
| `traefik_public` | traefik, app |
| `smpi_v1_internal` | app, postgresql, redis, rabbitmq, evolution_redis, evolution_api, celery_worker, celery_beat |
| `smpi_v1_egress` | evolution_api, celery_worker, celery_beat |

## Design system

Referência visual em `design_system/design-system.html` (abrir no navegador). Baseado no sistema FIESC.

- **Fonte:** MuseoSans (300/500/700)
- **Cor primária:** `--fsi-clr-1: hsl(220 74% 33%)`
- **Background:** `--fsi-clr-5: hsl(0 0% 96%)`
- **Border radius padrão:** `--fsi-border-rad: 20px`
- Todos os tokens estão prefixados com `--fsi-` e `--fs-`

Todos os templates devem incluir **VLibras**, HTML semântico e foco visível para WCAG.

## Documentação

A pasta `docs/` contém a documentação do projeto. Consulte `docs/README.md` para o índice. O **PRD.md** na raiz é a fonte de verdade para requisitos, modelo de dados e backlog de sprints.
