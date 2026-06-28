# Variáveis de ambiente (deploy)

Referência completa em [docs/environment.md](../environment.md).

Esta página resume apenas os valores específicos de **produção** para `www.techteo.com.br`.

## `.env` de produção (valores não-sensíveis)

```env
DEBUG=False
DOMAIN=www.techteo.com.br
ALLOWED_HOSTS=www.techteo.com.br,techteo.com.br,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=https://www.techteo.com.br,https://techteo.com.br

POSTGRES_DB=smpi
POSTGRES_USER=smpi
POSTGRES_HOST=postgresql
POSTGRES_PORT=5432

RABBITMQ_DEFAULT_USER=smpi
RABBITMQ_HOST=rabbitmq
REDIS_HOST=redis

LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
EMBEDDINGS_MODEL=text-embedding-3-small

EVOLUTION_API_URL=http://evolution_api:8080
EVOLUTION_INSTANCE=smpi

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu@email.com
EMAIL_HOST_PASSWORD=senha-de-app-gmail

IMAGE=smpi_app:latest
```

## Docker Secrets (valores sensíveis)

| Secret | Conteúdo |
|---|---|
| `smpi_django_secret` | SECRET_KEY do Django (50+ chars aleatórios) |
| `smpi_db_password` | Senha do PostgreSQL |
| `smpi_redis_password` | Senha do Redis |
| `smpi_rabbit_password` | Senha do RabbitMQ |
| `smpi_evolution_redis_password` | Senha do Redis dedicado da Evolution API |
| `smpi_openai_key` | `sk-...` (chave OpenAI) |
| `smpi_evolution_key` | API key da Evolution API |
| `CLOUDFLARE_DNS_API_TOKEN` | Token Cloudflare para DNS-01 |

Ver guia completo de criação em [deploy/swarm.md](swarm.md#3-criar-docker-secrets).
