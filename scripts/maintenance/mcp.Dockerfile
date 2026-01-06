FROM python:3.11-slim

WORKDIR /app

# Prevent python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Copy only the MCP package and dependencies logic first (caching)
COPY scripts/maintenance/evolution_mcp /app/scripts/maintenance/evolution_mcp

# Install dependencies
# We list them explicitly here to avoid copying full requirements.txt which might have heavy web deps
RUN pip install --no-cache-dir \
    "mcp[cli]" \
    httpx \
    pydantic \
    pydantic-settings \
    tenacity \
    uvicorn

# Expose SSE port
EXPOSE 8001

# Run the SSE server
CMD ["python", "scripts/maintenance/evolution_mcp/main.py"]
