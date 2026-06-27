#!/bin/bash
# Deploy SMPI to Docker Swarm.
# Usage: STACK_NAME=smpi_v1 ./scripts/deploy.sh
set -euo pipefail

STACK="${STACK_NAME:-smpi_v1}"
COMPOSE_FILE="stack.yml"

echo "[deploy] Building image..."
docker build -t smpi_app:latest .

echo "[deploy] Deploying stack: ${STACK}..."
docker stack deploy -c "${COMPOSE_FILE}" "${STACK}" --with-registry-auth

echo "[deploy] Waiting for app service to settle..."
sleep 10
docker service ls | grep "${STACK}"

echo "[deploy] Done."
