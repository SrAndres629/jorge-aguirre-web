# Usa Python 3.11 Slim como base
FROM python:3.11-slim

# Evita que Python escriba archivos .pyc y habilita logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instala dependencias del sistema necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Configura el directorio de trabajo
WORKDIR /app

# --- CAPA DE DEPENDENCIAS ---
# Copiamos primero el requirements.txt desde la nueva ubicación (natalia-brain)
COPY natalia-brain/requirements.txt .

# Instalamos las dependencias
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# --- CAPA DE CÓDIGO ---
# Copiamos todo el código del cerebro
COPY natalia-brain/ .

# Creamos un usuario no-root por seguridad
RUN addgroup --system jorgeuser && adduser --system --group jorgeuser
USER jorgeuser

# Exponemos el puerto (Render usa 10000 por defecto)
EXPOSE 10000

# Comando de inicio robusto (Uvicorn)
# Nota: Ajustado a main:app porque main.py está en la raíz de natalia-brain
CMD sh -c "uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000}"
