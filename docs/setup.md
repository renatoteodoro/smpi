# Configuração local

## Pré-requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (inclui Docker Compose)
- Git

> Para desenvolvimento sem Docker, veja a seção [Sem Docker](#sem-docker) no final desta página.

## Com Docker (recomendado)

### 1. Clonar e configurar

```bash
git clone https://github.com/renatoteodoro/smpi.git
cd smpi

# Copiar template de variáveis e preencher
cp .env.example .env
```

Abra o `.env` e preencha no mínimo:

```
OPENAI_API_KEY=sk-...          # obrigatório para o pipeline de IA
POSTGRES_PASSWORD=senha_local  # qualquer senha para desenvolvimento
REDIS_PASSWORD=senha_redis
RABBITMQ_DEFAULT_PASS=senha_rabbit
EVOLUTION_API_KEY=qualquer-chave-local
```

### 2. Subir a stack

```bash
docker compose up -d
```

Isso sobe: **app** (Django + Gunicorn), **postgresql** (PostgreSQL 16 + pgvector), **redis**, **rabbitmq**, **celery_worker**, **celery_beat** e **evolution_api** (WhatsApp).

Aguarde alguns segundos e verifique que tudo subiu:

```bash
docker compose ps
```

### 3. Migrações e superusuário (apenas na primeira vez)

```bash
docker exec smpi-app-1 python manage.py migrate_with_lock
docker exec smpi-app-1 python manage.py createsuperuser
```

### 4. (Opcional) Importar dados históricos

```bash
# 166.796 leituras de sensor do banner.csv
docker exec smpi-app-1 python manage.py import_banner

# Indexar documentos para RAG (coloque os arquivos PDF/DOCX/TXT em data/)
docker exec smpi-app-1 python manage.py ingest_documents --dir data/
```

### 5. Acessar

| URL | Descrição |
|---|---|
| http://localhost:8000 | Aplicação principal |
| http://localhost:8000/admin/ | Django Admin |
| http://localhost:8000/api/docs/ | Swagger UI |
| http://localhost:8000/health/ | Healthcheck |
| http://localhost:15672 | RabbitMQ Management (smpi / senha do .env) |
| http://localhost:8080/manager | Evolution API Manager (WhatsApp) |

### Logs e debug

```bash
# Logs da aplicação
docker logs smpi-app-1 -f

# Logs do Celery worker
docker logs smpi-celery_worker-1 -f

# Shell Django
docker exec -it smpi-app-1 python manage.py shell

# Reiniciar apenas o app após mudanças em settings
docker compose restart app
```

### Atualizar após mudanças no código

O volume `.:/app` monta o código-fonte e o Gunicorn usa `--reload`, então alterações em templates e views são refletidas imediatamente. Para mudanças em `settings.py` ou novos apps, reinicie:

```bash
docker compose restart app celery_worker
```

---

## Sem Docker

Para quem prefere rodar o Django diretamente no host (útil para debugging interativo):

### Pré-requisitos adicionais

- Python 3.13
- PostgreSQL 16 com extensão `pgvector`
- Redis 7
- RabbitMQ 3

### Instalação

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
```

Configure o `.env` com `POSTGRES_HOST=localhost`, `REDIS_URL=redis://localhost:6379/1`, etc.

```bash
python manage.py migrate_with_lock
python manage.py createsuperuser
python manage.py runserver
```

Celery em terminais separados:

```bash
celery -A core worker -l info
celery -A core beat -l info
```
