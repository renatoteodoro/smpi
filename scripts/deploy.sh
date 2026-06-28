#!/bin/bash
# Deploy SMPI para Docker Swarm.
#
# Uso:
#   ./scripts/deploy.sh              — git pull + build + deploy
#   ./scripts/deploy.sh --skip-build — deploy sem rebuild (usa imagem existente)
#
# Variáveis de ambiente:
#   IMAGE       — nome da imagem (default: smpi_app:latest para single-node)
#                 Para multi-node: IMAGE=ghcr.io/usuario/smpi_v1:latest
#   STACK_NAME  — nome do stack (default: smpi_v1)
set -euo pipefail

STACK="${STACK_NAME:-smpi_v1}"
COMPOSE_FILE="stack.yml"
SKIP_BUILD=false

for arg in "$@"; do
  case $arg in
    --skip-build) SKIP_BUILD=true ;;
    *) echo "[WARN] Argumento desconhecido: $arg" ;;
  esac
done

# ── Carrega .env com parser seguro (não faz source, evita injeção de shell) ──
if [ -f ".env" ]; then
  while IFS='=' read -r key value; do
    [[ "$key" =~ ^[[:space:]]*# ]] && continue
    [[ -z "$key" ]] && continue
    export "$key"="$value"
  done < <(grep -E '^[A-Za-z_][A-Za-z0-9_]*=' .env)
fi

echo "=================================================="
echo " SMPI Deploy — Stack: $STACK"
echo " Imagem: ${IMAGE:-smpi_app:latest}"
echo " Domínio: ${DOMAIN:-NÃO CONFIGURADO}"
echo "=================================================="

# ════════════════════════════ PRÉ-CONDIÇÕES ══════════════════════════════════

fail() { echo "[ERRO] $1"; exit 1; }

# 1. Swarm ativo
swarm_state=$(docker info --format '{{.Swarm.LocalNodeState}}' 2>/dev/null || echo "inactive")
[ "$swarm_state" = "active" ] || fail "Docker Swarm não está ativo. Execute: docker swarm init --advertise-addr \$(curl -s ifconfig.me)"

# 2. Secrets obrigatórios
required_secrets="smpi_db_password smpi_redis_password smpi_rabbit_password smpi_evolution_redis_password smpi_django_secret smpi_openai_key smpi_evolution_key CLOUDFLARE_DNS_API_TOKEN"
for secret in $required_secrets; do
  docker secret inspect "$secret" &>/dev/null || \
    fail "Secret '$secret' não existe. Veja a seção 19.5 do PRD.md para criá-lo."
done

# 3. Redes obrigatórias
required_networks="traefik_public smpi_v1_egress"
for net in $required_networks; do
  docker network inspect "$net" &>/dev/null || \
    fail "Rede '$net' não existe. Execute: docker network create --driver overlay --attachable $net"
done

# 4. DEBUG=False obrigatório
[ "${DEBUG:-True}" = "False" ] || fail "DEBUG=${DEBUG:-True} no .env. Defina DEBUG=False antes do deploy."

# 5. Domínio configurado
[ -n "${DOMAIN:-}" ] || fail "DOMAIN não está definido no .env. Defina DOMAIN=www.techteo.com.br"
echo "${DOMAIN}" | grep -qP '\.' || fail "DOMAIN parece inválido: ${DOMAIN}"

echo "[OK] Todas as pré-condições verificadas."

# ════════════════════════════ BUILD & PUSH ════════════════════════════════════

IMAGE="${IMAGE:-smpi_app:latest}"

if [ "$SKIP_BUILD" = false ]; then
  echo ""
  echo "[deploy] Atualizando repositório..."
  git pull

  echo "[deploy] Build: $IMAGE"
  docker build -t "$IMAGE" .

  # Push apenas se a imagem tiver um registry (contém '/')
  if echo "$IMAGE" | grep -q '/'; then
    echo "[deploy] Push: $IMAGE"
    docker push "$IMAGE"
  else
    echo "[deploy] Imagem local '$IMAGE' — pulando push (single-node Swarm)."
    echo "         Para multi-node: IMAGE=ghcr.io/usuario/smpi_v1:latest ./scripts/deploy.sh"
  fi
else
  echo "[deploy] --skip-build: usando imagem existente."
fi

# ════════════════════════════ DEPLOY ═════════════════════════════════════════

echo ""
echo "[deploy] Aplicando stack: $STACK..."
IMAGE="$IMAGE" docker stack deploy -c "$COMPOSE_FILE" "$STACK" --with-registry-auth

echo "[deploy] Aguardando serviços subirem (30s)..."
sleep 30

# ════════════════════════════ ROLLOUT FORÇADO ════════════════════════════════

echo "[deploy] Forçando rollout de app, celery_worker e celery_beat..."
for svc in app celery_worker celery_beat; do
  full="${STACK}_${svc}"
  if docker service inspect "$full" &>/dev/null 2>&1; then
    docker service update --force "$full" &>/dev/null && echo "  ✓ $full" || echo "  ✗ $full (ignorado)"
  fi
done

# ════════════════════════════ STATUS FINAL ════════════════════════════════════

echo ""
echo "[deploy] Status dos serviços:"
docker service ls | grep "$STACK" || true

echo ""
echo "=================================================="
echo " Deploy concluído!"
echo " Verificar: curl -fsS https://${DOMAIN}/health/"
echo " Swagger:   https://${DOMAIN}/api/docs/"
echo " Admin:     https://${DOMAIN}/admin/"
echo "=================================================="
