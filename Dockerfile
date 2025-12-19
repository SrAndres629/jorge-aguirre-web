# =================================================================
# DOCKERFILE - Jorge Aguirre Flores Web
# Imagen optimizada para FastAPI en producción
# =================================================================

# Python 3.10 slim para menor tamaño de imagen
FROM python:3.10-slim

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
EXPOSE 80

# Health check para monitoreo
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80/ || exit 1

# Comando de inicio - Puerto 80 para producción
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
