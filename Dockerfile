FROM node:20-slim AS frontend

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
ENV NEXT_PUBLIC_API_URL=http://localhost:8000
RUN npm run build

FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Node.js from the node image
COPY --from=frontend /usr/local/bin/node /usr/local/bin/node
COPY --from=frontend /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -s /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm && \
    ln -s /usr/local/lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx

WORKDIR /app

# Install Python backend
COPY backend/pyproject.toml backend/pyproject.toml
COPY backend/altryx/ backend/altryx/
RUN pip install --no-cache-dir ./backend

# Create data directory
RUN mkdir -p /app/data/uploads

# Copy built frontend
COPY --from=frontend /app/.next .next
COPY --from=frontend /app/node_modules node_modules
COPY --from=frontend /app/package.json package.json
COPY --from=frontend /app/next.config.ts next.config.ts
COPY --from=frontend /app/public public

# Copy sample data
COPY sample-data/ /app/sample-data/

# Startup script
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

ENV ALTRYX_DATA_DIR=/app/data

CMD ["/app/start.sh"]
