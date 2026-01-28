# ÚNICA VERSIÓN OFICIAL: PROTOCOLO SURJECTIVE SYSTEM v4.0
FROM python:3.11-slim

# Evitar que Python genere archivos .pyc y habilitar logs instantáneos
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Instalar dependencias del sistema necesarias para psycopg2 y utilitarios
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Fase 1: Copia de dependencias desde la nueva ubicación oficial
COPY natalia-brain/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Fase 2: Copia del código fuente (natalia-brain/ -> /app/)
COPY natalia-brain/ .

# El WORKDIR ahora contiene app/main.py, app/inbox_manager.py, etc.
# Y también templates/ y static/ en la raíz de /app.

# Puerto dinámico inyectado por Render ($PORT)
# CMD ejecutado en shell form para expansión de variables
CMD sh -c "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}"
