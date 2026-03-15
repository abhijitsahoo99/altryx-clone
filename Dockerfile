FROM node:20-slim AS frontend

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Node.js from the node image
COPY --from=frontend /usr/local/bin/node /usr/local/bin/node

WORKDIR /app

# Install Python backend
COPY backend/pyproject.toml backend/pyproject.toml
COPY backend/altryx/ backend/altryx/
RUN pip install --no-cache-dir ./backend

# Create data directory
RUN mkdir -p /app/data/uploads

# Copy standalone Next.js output (includes node_modules it needs)
COPY --from=frontend /app/.next/standalone ./
COPY --from=frontend /app/.next/static .next/static
COPY --from=frontend /app/public public

# Copy sample data
COPY sample-data/ /app/sample-data/

# Startup script
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

ENV ALTRYX_DATA_DIR=/app/data
ENV BACKEND_URL=http://localhost:8000

CMD ["/app/start.sh"]
