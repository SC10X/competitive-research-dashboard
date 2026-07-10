# ── Stage 1: Build frontend ─────────────────────────────────────────────
FROM node:22-alpine AS frontend-builder

WORKDIR /app/frontend

RUN corepack enable && corepack prepare pnpm@10 --activate

COPY frontend/package.json frontend/pnpm-lock.yaml* ./
ENV PNPM_IGNORED_BUILD_SCRIPTS=""

RUN pnpm install --frozen-lockfile

COPY frontend/ ./
RUN pnpm build

# ── Stage 2: Production runtime ─────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/ ./backend/

# Overwrite with latest database (must be AFTER backend source COPY)
COPY backend/data/competitive_research.db ./backend/data/

# Copy built frontend
COPY --from=frontend-builder /app/frontend/dist/ ./frontend/dist/

# Ensure writable data dir for SQLite WAL
RUN mkdir -p /app/backend/data /app/backend/uploads && chmod 777 /app/backend/data /app/backend/uploads

EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
