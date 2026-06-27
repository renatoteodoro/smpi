#!/bin/bash
# PostgreSQL backup script. Run on the Swarm manager node.
# Usage: BACKUP_DIR=/backups ./scripts/backup.sh
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-/backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
FILE="${BACKUP_DIR}/smpi_${TIMESTAMP}.sql.gz"

mkdir -p "${BACKUP_DIR}"

echo "[backup] Dumping database to ${FILE}..."
docker exec "$(docker ps -q -f name=smpi_v1_postgresql)" \
    pg_dump -U "${POSTGRES_USER:-smpi}" "${POSTGRES_DB:-smpi}" | gzip > "${FILE}"

echo "[backup] Done: ${FILE}"

# Keep last 14 days
find "${BACKUP_DIR}" -name "smpi_*.sql.gz" -mtime +14 -delete
echo "[backup] Old backups cleaned."
