#!/bin/bash
set -e

# Function to wait for a TCP host:port
wait_for_port() {
  local name=$1 host=$2 port=$3
  echo "Waiting for $name..."
  while ! nc -z "$host" "$port"; do
    echo "Still waiting for $name ($host:$port)..."
    sleep 1
  done
}

wait_for_port "Postgres" db 5432
wait_for_port "Ollama" ollama 11434

echo "Dependencies are up. Starting Flask app..."

if [ "$FLASK_ENV" = "production" ]; then
  echo "Launching Gunicorn..."
  exec gunicorn -c gunicorn_config.py app.main:app
else
  echo "Launching Flask dev server..."
  exec flask run --host=0.0.0.0 --port=5000
fi
