#!/bin/bash
set -e

echo "Starting FastAPI backend on port 8000..."
uvicorn altryx.main:app --host 0.0.0.0 --port 8000 &

# Wait for backend to be ready
echo "Waiting for backend health check..."
for i in $(seq 1 30); do
  if curl -sf http://localhost:8000/api/health > /dev/null 2>&1; then
    echo "Backend is ready."
    break
  fi
  if [ "$i" -eq 30 ]; then
    echo "ERROR: Backend failed to start within 30 seconds."
    exit 1
  fi
  sleep 1
done

echo "Starting Next.js on port ${PORT:-3000}..."
exec node server.js
