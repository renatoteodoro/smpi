# Variáveis de ambiente

O arquivo `.env` na raiz do projeto contém todas as variáveis de ambiente. O `.env` é gitignored — nunca versione valores reais. Use `.env.example` como template.

Em **produção**, senhas e chaves de API são gerenciadas por **Docker Secrets** (ver seção abaixo). O `.env` de produção contém apenas configurações não-sensíveis.

---

## Django

| Variável | Dev | Prod | Descrição |
|---|---|---|---|
| `SECRET_KEY` | qualquer valor | via Secret `smpi_django_secret` | Chave secreta do Django |
| `DEBUG` | `True` | `False` | Modo debug |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1,app` | `www.techteo.com.br,techteo.com.br,localhost,127.0.0.1` | Hosts permitidos (vírgula) |
| `CSRF_TRUSTED_ORIGINS` | `http://localhost:8000` | `https://www.techteo.com.br,https://techteo.com.br` | Origens CSRF confiáveis |
| `DOMAIN` | `localhost` | `www.techteo.com.br` | Domínio principal (usado pelo Traefik e Evolution API) |

## Localização

| Variável | Padrão | Descrição |
|---|---|---|
| `TIME_ZONE` | `America/Sao_Paulo` | Fuso horário |
| `LANGUAGE_CODE` | `pt-br` | Idioma padrão |

## Banco de dados (PostgreSQL)

| Variável | Dev | Prod | Descrição |
|---|---|---|---|
| `POSTGRES_DB` | `smpi` | `smpi` | Nome do banco |
| `POSTGRES_USER` | `smpi` | `smpi` | Usuário |
| `POSTGRES_PASSWORD` | `smpi_dev_password` | via Secret `smpi_db_password` | Senha |
| `POSTGRES_HOST` | `localhost` | `postgresql` | Host (nome do serviço Docker) |
| `POSTGRES_PORT` | `5432` | `5432` | Porta |
| `DATABASE_URL` | `postgresql://smpi:senha@localhost:5432/smpi` | gerado via secrets | URL completa (alternativa) |

## RabbitMQ

| Variável | Dev | Prod |
|---|---|---|
| `RABBITMQ_DEFAULT_USER` | `smpi` | `smpi` |
| `RABBITMQ_DEFAULT_PASS` | `smpi_rabbit_pass` | via Secret `smpi_rabbit_password` |
| `RABBITMQ_HOST` | `localhost` | `rabbitmq` |

## Celery / Redis

| Variável | Dev | Prod | Descrição |
|---|---|---|---|
| `CELERY_BROKER_URL` | `amqp://smpi:pass@localhost:5672/` | gerado via secrets | URL do broker |
| `CELERY_RESULT_BACKEND` | `redis://:pass@localhost:6379/0` | gerado via secrets | Backend de resultados |
| `REDIS_URL` | `redis://:pass@localhost:6379/1` | gerado via secrets | Redis para cache |
| `REDIS_PASSWORD` | `smpi_redis_pass` | via Secret `smpi_redis_password` | Senha do Redis |
| `REDIS_HOST` | `localhost` | `redis` | Host do Redis |

## IA / LLM

| Variável | Padrão | Descrição |
|---|---|---|
| `OPENAI_API_KEY` | — | Chave OpenAI · via Secret `smpi_openai_key` em prod |
| `LLM_PROVIDER` | `openai` | Provider do LLM (`openai` \| `local`) |
| `LLM_MODEL` | `gpt-4o-mini` | Modelo LLM (ex.: `gpt-4o-mini`, `gpt-4o`) |
| `EMBEDDINGS_MODEL` | `text-embedding-3-small` | Modelo de embeddings |
| `ANTHROPIC_API_KEY` | — | Opcional (Anthropic) |
| `LANGSMITH_API_KEY` | — | Opcional (tracing LangSmith) |

## Evolution API (WhatsApp)

| Variável | Dev | Prod | Descrição |
|---|---|---|---|
| `EVOLUTION_API_URL` | `http://localhost:8080` | `http://evolution_api:8080` | URL da Evolution API |
| `EVOLUTION_API_KEY` | `smpi-evolution-key-2024` | via Secret `smpi_evolution_key` | API key da Evolution |
| `EVOLUTION_INSTANCE` | `smpi` | `smpi` | Nome da instância WhatsApp |
| `EVOLUTION_REDIS_PASSWORD` | `smpi_redis_pass` | via Secret `smpi_evolution_redis_password` | Senha do Redis dedicado |

## E-mail (SMTP)

| Variável | Dev | Prod | Descrição |
|---|---|---|---|
| `EMAIL_BACKEND` | `console.EmailBackend` | `smtp.EmailBackend` | Backend de e-mail |
| `EMAIL_HOST` | `smtp.gmail.com` | seu SMTP | Servidor SMTP |
| `EMAIL_PORT` | `587` | `587` | Porta |
| `EMAIL_USE_TLS` | `True` | `True` | TLS |
| `EMAIL_HOST_USER` | — | seu e-mail | Usuário SMTP |
| `EMAIL_HOST_PASSWORD` | — | senha de app | Senha SMTP |

## Imagem Docker (deploy)

| Variável | Dev | Prod single-node | Prod multi-node |
|---|---|---|---|
| `IMAGE` | `smpi_app:latest` | `smpi_app:latest` | `ghcr.io/usuario/smpi_v1:latest` |

---

## Docker Secrets (produção)

Em produção, as senhas nunca ficam no `.env`. São criadas como Docker Secrets e lidas pelo `settings.py` a partir de `/run/secrets/`:

| Secret | Variável equivalente | Como criar |
|---|---|---|
| `smpi_django_secret` | `SECRET_KEY` | `printf '%s' "$(openssl rand -base64 50)" \| docker secret create smpi_django_secret -` |
| `smpi_db_password` | `POSTGRES_PASSWORD` | `printf '%s' "$(openssl rand -base64 32)" \| docker secret create smpi_db_password -` |
| `smpi_redis_password` | `REDIS_PASSWORD` | `printf '%s' "$(openssl rand -base64 32)" \| docker secret create smpi_redis_password -` |
| `smpi_rabbit_password` | `RABBITMQ_DEFAULT_PASS` | `printf '%s' "$(openssl rand -base64 32)" \| docker secret create smpi_rabbit_password -` |
| `smpi_evolution_redis_password` | `EVOLUTION_REDIS_PASSWORD` | `printf '%s' "$(openssl rand -base64 32)" \| docker secret create smpi_evolution_redis_password -` |
| `smpi_openai_key` | `OPENAI_API_KEY` | `printf '%s' "sk-..." \| docker secret create smpi_openai_key -` |
| `smpi_evolution_key` | `EVOLUTION_API_KEY` | `printf '%s' "api_key" \| docker secret create smpi_evolution_key -` |
| `CLOUDFLARE_DNS_API_TOKEN` | — | `printf '%s' "cf_token" \| docker secret create CLOUDFLARE_DNS_API_TOKEN -` |

> O `settings.py` lê `/run/secrets/<nome>` primeiro; se não existir, cai no valor do `.env`. Isso garante que dev e prod usem o mesmo código sem alteração.

## Notas de segurança

- Nunca use `source .env` em scripts shell — caracteres como `&`, `$`, `*` e `@` quebram o shell. Use um parser de `KEY=VALUE` (como o `deploy.sh`).
- O `.env` está no `.gitignore`; versione apenas `.env.example`.
- Em produção, o `.env` contém apenas configurações não-sensíveis (hosts, domínio, nomes de banco). Senhas ficam nos Secrets.
