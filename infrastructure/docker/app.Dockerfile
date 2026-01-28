# ÚNICA VERSIÓN OFICIAL: PROTOCOLO SURJECTIVE SYSTEM v4.0
# Usa Python 3.11 Slim
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Añadimos /app al PYTHONPATH
ENV PYTHONPATH=/app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiamos requirements
COPY natalia-brain/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiamos TODO el contenido de natalia-brain a la raíz /app
COPY natalia-brain/ .

RUN addgroup --system jorgeuser && adduser --system --group jorgeuser
USER jorgeuser

EXPOSE 10000

# 🔥 USA EL LANZADOR PYTHON DIRECTO
CMD ["python", "run.py"]
