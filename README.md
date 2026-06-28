# SMPI — Sistema de Manutenção Prescritiva Inteligente

Plataforma web para manutenção **preditiva e prescritiva** de equipamentos industriais. Recebe eventos de sensores de vibração, identifica defeitos por similaridade vetorial e gera recomendações fundamentadas na base documental da empresa — sem alucinação.

> **Status:** Sprints 0–12 implementados · Pronto para deploy em `www.techteo.com.br`

## Funcionalidades

- **Pipeline prescritivo** — LangGraph 9 nós: pré-processamento → similaridade pgvector → RAG → LLM → prescrição grounded
- **Anti-alucinação** — regra de guarda obrigatória: sem documentação → reporta e solicita cadastro, nunca inventa
- **Chat com IA** — stream SSE token a token + chatbot flutuante em todas as telas
- **WhatsApp** — técnico de campo envia evento/consulta pelo WhatsApp, recebe recomendação em segundos
- **Dashboard** — KPIs, gráficos Chart.js, ranking de equipamentos, insights com IA
- **Relatórios** — exportação PDF (Reportlab) e CSV
- **API REST** — ingestão autenticada por API key, Swagger em `/api/docs/`
- **Acessibilidade** — VLibras, HTML semântico, WCAG

## Stack

| Camada | Tecnologia |
|---|---|
| Backend | Python 3.13 · Django 6.0 · Django REST Framework |
| IA | LangGraph · LangChain · sentence-transformers (embeddings locais) |
| LLM | gpt-4o-mini via OpenAI (configurável via `LLM_MODEL`) |
| Banco | PostgreSQL 16 + pgvector |
| Async | Celery · RabbitMQ · Redis |
| WhatsApp | Evolution API v2 |
| Infra | Docker Swarm · Traefik · TLS wildcard DNS-01/Cloudflare |

## Início rápido (desenvolvimento)

```bash
# 1. Variáveis de ambiente
cp .env.example .env
# Editar .env: preencher OPENAI_API_KEY e verificar as senhas padrão

# 2. Subir toda a stack local
docker compose up -d

# 3. Migrações e superusuário (apenas na primeira vez)
docker exec smpi-app-1 python manage.py migrate_with_lock
docker exec smpi-app-1 python manage.py createsuperuser

# 4. (Opcional) Importar dados históricos — 166k leituras do banner.csv
docker exec smpi-app-1 python manage.py import_banner

# 5. (Opcional) Indexar documentos para RAG
docker exec smpi-app-1 python manage.py ingest_documents --dir data/
```

Acesse em **http://localhost:8000** · Admin em **http://localhost:8000/admin/**

## Deploy em produção

```bash
# Na VPS (Ubuntu 22.04/24.04):
docker swarm init
docker network create --driver overlay --attachable traefik_public
docker network create --driver overlay --internal smpi_v1_internal
docker network create --driver overlay smpi_v1_egress

# Criar secrets (senhas reais, nunca versionar)
printf '%s' "senha_forte" | docker secret create smpi_db_password -
printf '%s' "senha_forte" | docker secret create smpi_redis_password -
printf '%s' "senha_forte" | docker secret create smpi_rabbit_password -
printf '%s' "senha_forte" | docker secret create smpi_evolution_redis_password -
printf '%s' "chave_forte" | docker secret create smpi_django_secret -
printf '%s' "sk-..."      | docker secret create smpi_openai_key -
printf '%s' "api_key"     | docker secret create smpi_evolution_key -
printf '%s' "cf_token"    | docker secret create CLOUDFLARE_DNS_API_TOKEN -

# Configurar .env de produção (ver docs/deploy/swarm.md)
# Executar deploy
DOMAIN=www.techteo.com.br ./scripts/deploy.sh
```

Veja o guia completo em [`docs/deploy/swarm.md`](docs/deploy/swarm.md).

## Documentação

| Documento | Descrição |
|---|---|
| [Visão geral](docs/overview.md) | Objetivos, personas e KPIs |
| [Configuração local](docs/setup.md) | Docker + dev sem Docker |
| [Arquitetura](docs/architecture/overview.md) | Stack, apps, fluxo principal |
| [Pipeline IA](docs/architecture/ai-pipeline.md) | LangGraph, RAG, regra de guarda |
| [Modelo de dados](docs/architecture/data-model.md) | ER, campos principais |
| [API REST](docs/api/index.md) | Endpoints, autenticação, exemplos |
| [Deploy Swarm](docs/deploy/swarm.md) | Guia completo de deploy em produção |
| [Variáveis de ambiente](docs/environment.md) | Referência de todas as variáveis |
| [Comandos úteis](docs/dev/commands.md) | Django management, Docker, Celery |
| [Design System](docs/design-system.md) | Tokens visuais FIESC, tipografia |

A documentação também está disponível online em **https://www.techteo.com.br/docs/** (via MkDocs Material).
