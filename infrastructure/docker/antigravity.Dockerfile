FROM python:3.11-slim-bookworm

# Evitar prompts durante la instalación
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    git \
    curl \
    openssh-server \
    sudo \
    build-essential \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Configurar SSH
RUN mkdir /var/run/sshd
RUN useradd -m -s /bin/bash agent && \
    echo 'agent:antigravity' | chpasswd && \
    adduser agent sudo && \
    echo 'agent ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

# Instalar Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Instalar Aider
RUN pip install --no-cache-dir aider-chat

# Directorio de trabajo
WORKDIR /app

# Copiar script de entrada
COPY infrastructure/docker/entrypoint-antigravity.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Exponer SSH
EXPOSE 22

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
