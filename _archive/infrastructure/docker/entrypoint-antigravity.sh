#!/bin/bash

echo "🚀 Iniciando Ecosistema Antigravity..."

# Iniciar Ollama en segundo plano
ollama serve > /var/log/ollama.log 2>&1 &

# Esperar a que Ollama esté listo
echo "⏳ Esperando a que Ollama inicie..."
until curl -s http://localhost:11434/api/tags > /dev/null; do
    sleep 2
done

# Descargar modelo Qwen 2.5 Coder
echo "🧠 Cargando cerebro: Qwen 2.5 Coder (7b)..."
ollama pull qwen2.5-coder:7b

# Iniciar Servidor SSH
echo "🛡️ Iniciando servidor SSH (Puerto 22)..."
/usr/sbin/sshd -D
