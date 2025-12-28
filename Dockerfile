# =================================================================
# DOCKERFILE - Jorge Aguirre Flores Web
# Imagen optimizada para FastAPI en producción
# =================================================================

# Python 3.11 slim para mejor performance
FROM python:3.11-slim

# Variables de entorno para Python optimizado
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=80

# Directorio de trabajo
WORKDIR /app

# Copiar requirements primero (mejor cache de Docker)
COPY requirements.txt .

# Instalar dependencias sin cache para menor tamaño
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Puerto que expone la aplicación
EXPOSE $PORT

# Health check para monitoreo
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/ || exit 1

# Comando de inicio - Gunicorn para producción
CMD sh -c "gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:$PORT"
