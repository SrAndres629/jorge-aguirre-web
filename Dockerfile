# =================================================================
# DOCKERFILE - Jorge Aguirre Flores Web
# Arquitectura: Multi-Stage Build (Builder -> Runtime)
# Nivel: Producción / Militar
# =================================================================

# -----------------------------------------------------------------
# ETAPA 1: BUILDER (Compilación y dependencias)
# -----------------------------------------------------------------
FROM python:3.11-slim as builder

WORKDIR /app

# Variables de entorno para build
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalar dependencias de sistema necesarias para compilar algunas librerías
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar y compilar dependencias Python en un entorno virtual o directorio específico
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# -----------------------------------------------------------------
# ETAPA 2: RUNNER (Imagen final ligera)
# -----------------------------------------------------------------
FROM python:3.11-slim as runner

WORKDIR /app

# Instalar dependencias mínimas de sistema para runtime (curl para healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar wheels compiladas desde la etapa builder e instalar
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache-dir /wheels/*

# Copiar el código fuente de la aplicación
COPY . .

# Crear un usuario no-root para seguridad
RUN addgroup --system jorgeuser && adduser --system --group jorgeuser
USER jorgeuser

# Exponer el puerto
ENV PORT=80
EXPOSE $PORT

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/ || exit 1

# Comando de inicio optimizado (Gunicorn + Uvicorn Workers)
CMD sh -c "gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:$PORT"
