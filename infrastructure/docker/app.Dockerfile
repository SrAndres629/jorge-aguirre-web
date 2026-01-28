# =================================================================
# APP DOCKERFILE (Multi-Stage)
# Context: Project Root (.)
# =================================================================

# --- Stage 1: Builder ---
FROM python:3.11-slim AS builder

WORKDIR /build

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
# Install Python dependencies
COPY natalia-brain/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# --- Stage 2: Final Runtime ---
FROM python:3.11-slim

WORKDIR /app

# Environment Setup
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"
ENV PORT=10000
ENV MALLOC_ARENA_MAX=2

# Install runtime dependencies (curl for healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Setup Non-Root User
RUN addgroup --system jorgeuser && adduser --system --group jorgeuser

# Copy Application Code
COPY natalia-brain/ .

# Ensure database directory exists and has correct permissions
RUN mkdir -p /app/database && chown -R jorgeuser:jorgeuser /app

# Switch to User
USER jorgeuser

# Expose Port
EXPOSE 10000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Default Command (Use Shell form to expand $PORT)
CMD sh -c "uvicorn main:app --host 0.0.0.0 --port ${PORT}"
