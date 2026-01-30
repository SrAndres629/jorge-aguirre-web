
# =================================================================
# MCP DOCKERFILE
# Context: Project Root (.)
# =================================================================
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Install Dependencies
# We install these first to leverage cache if scripts change
RUN pip install --no-cache-dir \
    "mcp[cli]" \
    httpx \
    pydantic \
    pydantic-settings \
    tenacity \
    textual \
    httpcore

# Copy Scripts
# Note: Context is Root, so we copy from scripts/
COPY scripts/maintenance/evolution_mcp /app/scripts/maintenance/evolution_mcp
COPY scripts/maintenance/evolution_monitor_v4.py /app/scripts/maintenance/evolution_monitor_v4.py

# Expose Port for MCP
EXPOSE 8001

# Keep container alive
CMD ["tail", "-f", "/dev/null"]
