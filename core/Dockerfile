# =================================================================
# DOCKERFILE - Jorge Aguirre Flores Web
# Arquitectura: Production-Ready con Usuario No-Root
# =================================================================

FROM python:3.11-slim

WORKDIR /app

# Variables de entorno para Python optimizado
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Instalar dependencias de sistema mínimas
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero (mejor cache de Docker)
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Crear un usuario no-root para seguridad
RUN addgroup --system jorgeuser && adduser --system --group jorgeuser && \
    chown -R jorgeuser:jorgeuser /app

USER jorgeuser

# Puerto que expone la aplicación
EXPOSE $PORT

# Health check para monitoreo
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:$PORT/ || exit 1

# Comando de inicio predeterminado (Producción)
# Nota: Reducimos workers a 2 y aumentamos timeout a 90s para evitar OOM/Timeout en Render Free
CMD gunicorn -w 2 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:$PORT --timeout 90

