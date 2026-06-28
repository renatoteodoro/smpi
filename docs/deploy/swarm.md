# Deploy Docker Swarm — www.techteo.com.br

Guia completo para deploy do SMPI em produção usando Docker Swarm + Traefik.

## Pré-requisitos

- VPS Ubuntu 22.04/24.04 com acesso `sudo`
- Domínio `techteo.com.br` gerenciado pelo **Cloudflare**
- Docker Engine + Compose plugin instalados (ver abaixo)

## 1. Preparar o servidor

```bash
# Atualizar sistema
sudo apt-get update && sudo apt-get upgrade -y

# Instalar Docker
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Adicionar usuário ao grupo docker (reabra a sessão)
sudo usermod -aG docker "$USER"

# Firewall
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable
```

## 2. Inicializar Swarm e criar redes

```bash
# Inicializar Swarm (use o IP público da VPS)
docker swarm init --advertise-addr "$(curl -s ifconfig.me)"

# Criar as 3 redes obrigatórias
docker network create --driver overlay --attachable traefik_public
docker network create --driver overlay --internal smpi_v1_internal
docker network create --driver overlay smpi_v1_egress

# Verificar
docker network ls | grep -E 'traefik_public|smpi_v1_internal|smpi_v1_egress'
```

## 3. Criar Docker Secrets

Senhas nunca ficam em texto no `.env`. Crie-as como secrets antes do deploy:

```bash
# Cloudflare: crie o token em My Profile → API Tokens → Create Custom Token
# Permissão: Zone → DNS → Edit → techteo.com.br
printf '%s' "seu-cf-api-token" | docker secret create CLOUDFLARE_DNS_API_TOKEN -

# Senhas da stack (gere valores aleatórios)
printf '%s' "$(openssl rand -base64 32)" | docker secret create smpi_db_password -
printf '%s' "$(openssl rand -base64 32)" | docker secret create smpi_redis_password -
printf '%s' "$(openssl rand -base64 32)" | docker secret create smpi_rabbit_password -
printf '%s' "$(openssl rand -base64 32)" | docker secret create smpi_evolution_redis_password -
printf '%s' "$(openssl rand -base64 50)" | docker secret create smpi_django_secret -

# Chaves de API (cole o valor real, finalize com Enter + Ctrl-D)
docker secret create smpi_openai_key -
docker secret create smpi_evolution_key -

# Verificar
docker secret ls
```

## 4. Clonar o repositório e configurar `.env`

```bash
mkdir -p /opt/smpi && cd /opt/smpi
git clone https://github.com/renatoteodoro/smpi.git .

# Criar .env de produção
cat > .env << 'EOF'
DEBUG=False
DOMAIN=www.techteo.com.br
ALLOWED_HOSTS=www.techteo.com.br,techteo.com.br,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=https://www.techteo.com.br,https://techteo.com.br

# Banco
POSTGRES_DB=smpi
POSTGRES_USER=smpi
POSTGRES_HOST=postgresql
POSTGRES_PORT=5432

# RabbitMQ
RABBITMQ_DEFAULT_USER=smpi
RABBITMQ_HOST=rabbitmq

# Redis
REDIS_HOST=redis

# IA
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
EMBEDDINGS_MODEL=text-embedding-3-small

# Evolution API
EVOLUTION_API_URL=http://evolution_api:8080
EVOLUTION_INSTANCE=smpi

# E-mail (SMTP)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu@email.com
EMAIL_HOST_PASSWORD=senha-de-app-gmail

# Imagem
IMAGE=smpi_app:latest
EOF

chmod 600 .env
```

> As senhas (`POSTGRES_PASSWORD`, `REDIS_PASSWORD`, `OPENAI_API_KEY`, etc.) **não entram no `.env`** — vêm dos Docker Secrets criados no passo 3.

## 5. Deploy

```bash
cd /opt/smpi
./scripts/deploy.sh
```

O script valida pré-condições (Swarm ativo, secrets existentes, redes criadas, `DEBUG=False`, `DOMAIN` configurado), faz o build e deploy.

Para deploys subsequentes sem rebuild:

```bash
./scripts/deploy.sh --skip-build
```

## 6. Conectar a Evolution API ao WhatsApp

A Evolution API roda na rede interna e não é exposta publicamente. Para acessar o Manager e escanear o QR code, use um tunnel SSH:

```bash
# No seu computador local:
ssh -L 8080:localhost:8080 usuario@ip-da-vps
```

Acesse http://localhost:8080/manager no seu navegador local:

1. Login com a API key do secret `smpi_evolution_key`
2. Clique em **New Instance** → nome: `smpi`
3. Clique em **Connect** → escaneie o QR code com o WhatsApp
4. Verifique: `Status` deve mostrar `open`

O webhook global já está configurado para `https://www.techteo.com.br/webhooks/whatsapp/` via variável de ambiente no `stack.yml`.

## 7. Verificações pós-deploy

```bash
# Healthcheck da aplicação
curl -fsS https://www.techteo.com.br/health/ && echo "OK"

# Certificado wildcard DNS-01
echo | openssl s_client -servername www.techteo.com.br -connect www.techteo.com.br:443 2>/dev/null \
  | openssl x509 -noout -subject -ext subjectAltName

# Redirect http → https
curl -I http://www.techteo.com.br/health/

# Swagger
curl -fsS -o /dev/null -w "Swagger: %{http_code}\n" https://www.techteo.com.br/api/docs/

# Logs do Traefik (confirmar emissão ACME)
docker service logs smpi_v1_traefik 2>&1 | grep -iE 'certificate|acme|dns'

# Status dos serviços
docker service ls | grep smpi_v1
```

## 8. Backup

```bash
./scripts/backup.sh
```

Faz dump do PostgreSQL e compacta. Rotação automática de 14 dias.

## Troubleshooting

**Certificado não emitido:**
- Confirmar que o Cloudflare está como DNS autoritativo para `techteo.com.br`
- Verificar se o token Cloudflare tem permissão `Zone → DNS → Edit`
- Logs: `docker service logs smpi_v1_traefik 2>&1 | grep -i acme`

**App não responde:**
- `docker service ps smpi_v1_app` para ver erros de deploy
- `docker service logs smpi_v1_app --follow`

**Celery não processa tarefas:**
- `docker service logs smpi_v1_celery_worker --follow`
- Verificar se o secret `smpi_rabbit_password` existe: `docker secret inspect smpi_rabbit_password`

**Evolution API não recebe mensagens:**
- Verificar conexão: `curl http://localhost:8080/instance/connectionState/smpi -H "apikey: SUA_CHAVE"`
- Webhook configurado: `curl http://localhost:8080/webhook/find/smpi -H "apikey: SUA_CHAVE"`
