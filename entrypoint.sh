#!/bin/sh
set -e

host="${DB_HOST:-db}"
port="${DB_PORT:-5432}"

echo "Waiting for database to be ready on $host:$port..."
until nc -z "$host" "$port"; do
  echo "Database is unavailable - sleeping"
  sleep 1
done
echo "Database is ready, continuing."

if [ $# -gt 0 ]; then
  echo "Executing custom command: $@"
  exec "$@"
fi

echo "Applying database migrations..."
poetry run alembic upgrade head

echo "Starting application..."
exec gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
