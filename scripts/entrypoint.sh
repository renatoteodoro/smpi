#!/bin/bash
set -e

echo "[entrypoint] Waiting for database..."
python manage.py wait_for_db

echo "[entrypoint] Running migrations (with advisory lock)..."
python manage.py migrate_with_lock

echo "[entrypoint] Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "[entrypoint] Starting server..."
exec "$@"
