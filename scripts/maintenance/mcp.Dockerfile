FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

RUN pip install --no-cache-dir --upgrade pip

# Copy MCP package
COPY scripts/maintenance/evolution_mcp /app/scripts/maintenance/evolution_mcp

# Install dependencies
RUN pip install --no-cache-dir \
    "mcp[cli]" \
    httpx \
    pydantic \
    pydantic-settings \
    tenacity

# Expose port for potential HTTP endpoints
EXPOSE 8001

# Keep container alive for manual MCP access
CMD ["tail", "-f", "/dev/null"]
