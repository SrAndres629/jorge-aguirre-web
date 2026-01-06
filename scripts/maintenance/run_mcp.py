
import uvicorn
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from scripts.maintenance.evolution_mcp.main import mcp

# This wrapper allows deploying the FastMCP as a web service (SSE)
# accessible by n8n or other agents via HTTP

def create_app():
    return mcp.sse_app

if __name__ == "__main__":
    print("🚀 Starting Evolution MCP Server on port 8001 (SSE)...")
    uvicorn.run(create_app, host="0.0.0.0", port=8001)
