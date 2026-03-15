FROM node:20-slim AS frontend

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
ENV NEXT_PUBLIC_API_URL=http://localhost:8000
RUN npm run build

FROM python:3.11-slim

# Copy Node.js from the node image
COPY --from=frontend /usr/local/bin/node /usr/local/bin/node
COPY --from=frontend /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -s /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm

WORKDIR /app

# Install Python backend
COPY backend/pyproject.toml backend/pyproject.toml
COPY backend/altryx/ backend/altryx/
RUN pip install --no-cache-dir ./backend

# Copy built frontend
COPY --from=frontend /app/.next .next
COPY --from=frontend /app/node_modules node_modules
COPY --from=frontend /app/package.json package.json
COPY --from=frontend /app/public public

# Startup script
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

CMD ["/app/start.sh"]
