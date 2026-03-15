#!/bin/bash
set -e

# Start the FastAPI backend on port 8000
uvicorn altryx.main:app --host 0.0.0.0 --port 8000 &

# Start Next.js on the Railway-assigned PORT (or 3000)
PORT=${PORT:-3000} exec npm start
