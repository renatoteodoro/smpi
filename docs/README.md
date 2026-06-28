# SMPI — Documentação

Sistema de Manutenção Prescritiva Inteligente · Sprints 0–12 implementados.

## Índice

| Documento | Descrição |
|---|---|
| [Visão geral](overview.md) | O que é o SMPI, objetivos e personas |
| [Configuração local](setup.md) | Como rodar o projeto em desenvolvimento |
| [Arquitetura — visão geral](architecture/overview.md) | Stack, apps e fluxo principal |
| [Arquitetura — Pipeline IA](architecture/ai-pipeline.md) | LangGraph, RAG, nós e regra de guarda |
| [Arquitetura — Modelo de dados](architecture/data-model.md) | ER e campos principais |
| [API REST](api/index.md) | Endpoints, autenticação, exemplos |
| [Deploy Docker Swarm](deploy/swarm.md) | Guia completo de deploy em produção |
| [Variáveis de ambiente](environment.md) | Referência de todas as variáveis e Docker Secrets |
| [Comandos úteis](dev/commands.md) | Django management, Docker, Celery |
| [Design System](design-system.md) | Tokens visuais FIESC, tipografia e componentes |

## Estado do projeto

**Sprints 0–12 concluídos.** A stack completa está operacional:

```
smpi/
├── core/            — projeto Django, settings, /health/
├── base/            — TimeStampedModel, mixins, middleware de media
├── accounts/        — Custom User, login por e-mail, papéis
├── assets/          — Equipment, MeasurementPoint
├── monitoring/      — SensorReading (166k registros), ingestão REST/CSV/manual
├── faults/          — catálogo de defeitos com is_problem
├── knowledge/       — KnowledgeDocument, DocumentChunk, RAG + OCR
├── prescriptions/   — Prescription, pipeline LangGraph 9 nós
├── analytics/       — Dashboard KPIs + Chart.js
├── reports/         — exportação PDF/CSV
├── ai/              — agente LangGraph, 8 ferramentas, chat SSE
├── notifications/   — notificações in-app
├── whatsapp/        — webhook + envio via Evolution API v2
├── api/             — DRF + drf-spectacular (Swagger /api/docs/)
├── scripts/         — entrypoint.sh, deploy.sh, backup.sh
├── stack.yml        — Docker Swarm produção (Traefik embutido)
├── docker-compose.yml — desenvolvimento local
└── PRD.md           — fonte de verdade para requisitos
```

> Para o plano completo e backlog de sprints, consulte o [PRD.md](../PRD.md).
