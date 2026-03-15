#!/bin/bash
set -e

# Start the FastAPI backend on port 8000
uvicorn altryx.main:app --host 0.0.0.0 --port 8000 &

# Wait for backend to be ready
for i in $(seq 1 30); do
  if curl -sf http://localhost:8000/api/health > /dev/null 2>&1; then
    break
  fi
  sleep 1
done

# Start Next.js standalone server on the Railway-assigned PORT (or 3000)
exec node server.js
