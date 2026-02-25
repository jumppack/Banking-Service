#!/usr/bin/env sh
set -e

echo "Running Alembic migrations..."
alembic upgrade head

echo "Starting Banking Service API..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${API_PORT:-8000}
