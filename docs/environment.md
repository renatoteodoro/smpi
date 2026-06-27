# Variáveis de ambiente

O arquivo `.env` na raiz do projeto contém todas as variáveis necessárias. O arquivo é gitignored — nunca versione valores reais.

## Django

| Variável | Exemplo | Descrição |
|---|---|---|
| `SECRET_KEY` | — | Chave secreta do Django. Gere com `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `DEBUG` | `True` | `False` em produção |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Hosts permitidos (separados por vírgula) |
| `CSRF_TRUSTED_ORIGINS` | `http://localhost:8000` | Origens confiáveis para CSRF |

## Localização

| Variável | Exemplo | Descrição |
|---|---|---|
| `TIME_ZONE` | `America/Sao_Paulo` | Fuso horário |
| `LANGUAGE_CODE` | `pt-br` | Idioma padrão |

## Banco de dados (PostgreSQL)

| Variável | Exemplo | Descrição |
|---|---|---|
| `POSTGRES_DB` | `smpi` | Nome do banco |
| `POSTGRES_USER` | `smpi` | Usuário |
| `POSTGRES_PASSWORD` | — | Senha |
| `DATABASE_URL` | `postgres://smpi:senha@localhost:5432/smpi` | URL completa (alternativa às variáveis individuais) |

## RabbitMQ

| Variável | Descrição |
|---|---|
| `RABBITMQ_DEFAULT_USER` | Usuário do RabbitMQ |
| `RABBITMQ_DEFAULT_PASS` | Senha do RabbitMQ |

## Celery / Redis

| Variável | Exemplo | Descrição |
|---|---|---|
| `CELERY_BROKER_URL` | `amqp://user:pass@localhost:5672/` | URL do broker (RabbitMQ) |
| `CELERY_RESULT_BACKEND` | `redis://localhost:6379/0` | Backend de resultados |
| `REDIS_URL` | `redis://localhost:6379/1` | Redis para cache do app |

## IA / LLM

| Variável | Descrição |
|---|---|
| `OPENAI_API_KEY` | Chave da API OpenAI (para GPT-5.5-mini) |
| `OPENAI_MODEL` | Modelo a usar (ex.: `gpt-5.5-mini`) |
| `ANTHROPIC_API_KEY` | Chave Anthropic (opcional) |
| `LANGSMITH_API_KEY` | Chave LangSmith para tracing (opcional) |

## E-mail (SMTP)

| Variável | Padrão dev | Descrição |
|---|---|---|
| `EMAIL_BACKEND` | `django.core.mail.backends.console.EmailBackend` | Em dev: imprime no console |
| `EMAIL_HOST` | — | Servidor SMTP |
| `EMAIL_PORT` | `587` | Porta SMTP |
| `EMAIL_HOST_USER` | — | Usuário SMTP |
| `EMAIL_HOST_PASSWORD` | — | Senha SMTP |

## Notas de segurança

- Em produção, as senhas e chaves são gerenciadas por **Docker Secrets**, não por `.env`.
- Nunca use `source .env` em scripts shell — caracteres como `&`, `$`, `*` e `@` quebram o shell. Use um parser de `KEY=VALUE`.
- O `.env` está no `.gitignore`; versione apenas `.env.example` com valores vazios.
