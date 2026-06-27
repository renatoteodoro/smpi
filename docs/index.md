# SMPI — Sistema de Manutenção Prescritiva Inteligente

O SMPI é uma plataforma web Django para manutenção preditiva e prescritiva de equipamentos industriais, com pipeline de IA baseado em LangGraph, RAG com pgvector, e integração WhatsApp via Evolution API.

> **Status:** Sprints 0–12 implementados · Python 3.13 · Django 6.0 · gpt-4o-mini

## Módulos

| Módulo | Descrição |
|---|---|
| `base` | `TimeStampedModel`, mixins de permissão, middleware |
| `accounts` | Autenticação por e-mail, perfis admin/maintenance/viewer |
| `assets` | Equipamentos (`Equipment`) e pontos de medição (`MeasurementPoint`) |
| `monitoring` | Leituras de sensor — 166.796 registros históricos importados |
| `faults` | Catálogo de defeitos com flag `is_problem` (estado vs problema) |
| `knowledge` | Base documental RAG: PDF/DOCX/TXT + OCR via GPT-4o Vision |
| `prescriptions` | Pipeline LangGraph 9 nós, geração de prescrições grounded |
| `analytics` | Dashboard KPIs + Chart.js |
| `reports` | Exportação PDF/CSV |
| `ai` | Agente LangGraph com 8 ferramentas, chat SSE + guardrail anti-alucinação |
| `notifications` | Notificações in-app |
| `whatsapp` | Webhook Evolution API |
| `api` | DRF + drf-spectacular (Swagger `/api/docs/`) |

## Início rápido

```bash
# Configurar ambiente
cp .env.example .env        # preencher OPENAI_API_KEY, POSTGRES_*, etc.
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt

# Banco e migrações
python manage.py migrate
python manage.py createsuperuser

# Importar dados históricos (banner.csv → 166k leituras)
python manage.py import_banner

# Indexar documentos para RAG
python manage.py ingest_documents --dir data/

# Servidor de desenvolvimento
python manage.py runserver
```

## Links rápidos

- **Admin:** `/admin/`
- **Swagger:** `/api/docs/`
- **Documentação:** `/docs/`
- **Saúde:** `/health/`
