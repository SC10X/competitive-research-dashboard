# ── Stage 1: Build frontend ─────────────────────────────────────────────
FROM node:22-alpine AS frontend-builder

WORKDIR /app/frontend

# Enable pnpm and configure to allow esbuild builds
RUN corepack enable && corepack prepare pnpm@10 --activate

COPY frontend/package.json frontend/pnpm-lock.yaml* ./

# Allow esbuild postinstall scripts (required by vite)
ENV PNPM_IGNORED_BUILD_SCRIPTS=""

RUN pnpm install --frozen-lockfile

COPY frontend/ ./
RUN pnpm build

# ── Stage 2: Production runtime ─────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Install only what we need
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/ ./backend/

# Copy built frontend
COPY --from=frontend-builder /app/frontend/dist/ ./frontend/dist/

# Copy the database (seeded with 469 brands)
COPY backend/data/competitive_research.db ./backend/data/

# Make sure data dir is writable for SQLite WAL files
RUN mkdir -p /app/backend/data /app/backend/uploads && chmod 777 /app/backend/data /app/backend/uploads

EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
