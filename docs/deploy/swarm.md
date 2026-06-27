# Deploy Docker Swarm

## Pré-requisitos

- Docker Swarm inicializado (`docker swarm init`)
- Rede externa `traefik_public` criada (`docker network create -d overlay traefik_public`)
- Traefik configurado com DNS-01/Cloudflare para TLS wildcard

## Deploy

```bash
# 1. Criar .env de produção
cp .env.example .env
# Editar com valores reais: POSTGRES_PASSWORD, REDIS_PASSWORD, etc.

# 2. Buildar imagem
docker build -t smpi_app:latest .

# 3. Deploy do stack
STACK_NAME=smpi_v1 ./scripts/deploy.sh
```

## Verificar

```bash
docker service ls | grep smpi_v1
docker service logs smpi_v1_app --follow
```

## Redes

| Rede | Serviços |
|---|---|
| `traefik_public` | traefik, app |
| `smpi_v1_internal` | todos os serviços internos |
| `smpi_v1_egress` | evolution_api, celery_worker, celery_beat |
