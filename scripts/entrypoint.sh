#!/bin/bash
set -e

echo "[entrypoint] Waiting for database..."
python manage.py wait_for_db

echo "[entrypoint] Running migrations..."
python manage.py migrate --noinput

echo "[entrypoint] Collecting static files..."
python manage.py collectstatic --noinput

echo "[entrypoint] Starting server..."
exec "$@"
