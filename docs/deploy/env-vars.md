# Variáveis de Ambiente

Copie `.env.example` para `.env` e preencha os valores.

## Django

| Variável | Exemplo | Descrição |
|---|---|---|
| `SECRET_KEY` | `django-insecure-...` | Chave secreta Django |
| `DEBUG` | `True` | Modo debug (False em produção) |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Hosts permitidos |

## Banco de dados

| Variável | Exemplo |
|---|---|
| `POSTGRES_DB` | `smpi` |
| `POSTGRES_USER` | `smpi` |
| `POSTGRES_PASSWORD` | `senha_segura` |
| `POSTGRES_HOST` | `localhost` |
| `POSTGRES_PORT` | `5432` |

## Celery / Redis / RabbitMQ

| Variável | Exemplo |
|---|---|
| `CELERY_BROKER_URL` | `amqp://smpi:senha@localhost:5672/` |
| `REDIS_URL` | `redis://:senha@localhost:6379/0` |

## IA / LLM

| Variável | Exemplo | Descrição |
|---|---|---|
| `OPENAI_API_KEY` | `sk-...` | Chave API OpenAI |
| `LLM_PROVIDER` | `openai` | Provedor LLM |
| `LLM_MODEL` | `gpt-4o-mini` | Modelo a usar |
| `EMBEDDINGS_MODEL` | `paraphrase-multilingual-MiniLM-L12-v2` | Modelo de embeddings |

## WhatsApp

| Variável | Exemplo |
|---|---|
| `EVOLUTION_API_URL` | `http://localhost:8080` |
| `EVOLUTION_API_KEY` | `chave_secreta` |
| `EVOLUTION_INSTANCE` | `smpi` |
