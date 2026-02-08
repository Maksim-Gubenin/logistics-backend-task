#!/bin/sh
set -e

host="db"
port="5432"
timeout=15

echo "Waiting for database to be ready on $host:$port..."
until nc -z $host $port; do
  echo "Database is unavailable - sleeping"
  sleep 1
done
echo "Database is ready, continuing."

echo "Applying database migrations..."
poetry run alembic upgrade head

echo "Starting application..."
exec gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000