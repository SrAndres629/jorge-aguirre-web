import asyncio
import httpx
import logging
from app.config import settings

logger = logging.getLogger("heartbeat")

# TARGETS
# 1. Evolution API
TARGET_EVOLUTION = settings.EVOLUTION_API_URL
# 2. Natalia Brain (Self-Ping to keep Render awake)
# Using the Render default URL if available, else localhost (which doesn't help sleep but keeps event loop busy)
# Ideally getting the public URL from env or config. 
TARGET_BRAIN = "https://natalia-brain.onrender.com" # Hardcoded based on user context
# 3. Third Instance (n8n or Website)
TARGET_N8N = "https://jorge-aguirre-web.onrender.com" # Assuming this is the 'Website' or 3rd service.
# If the user meant n8n specifically:
# TARGET_N8N = settings.N8N_WEBHOOK_URL (if it's public)

async def start_heartbeat_hub():
    """
    💓 Triple-Node Keepalive System
    Pings all 3 critical services every 10 seconds to prevent Render spin-down.
    """
    logger.info("💓 HEARTBEAT HUB ACTIVATED. Frequency: 10s")
    
    # Define Targets
    targets = [
        {"name": "Evolution API", "url": f"{TARGET_EVOLUTION}/"},
        {"name": "Natalia Brain", "url": f"{TARGET_BRAIN}/api/health"},
        {"name": "Jorge Web/N8N", "url": TARGET_N8N} 
    ]

    async with httpx.AsyncClient(timeout=5.0) as client:
        while True:
            for target in targets:
                try:
                    # We just need to touch it. GET / or /health is enough.
                    await client.get(target["url"])
                    # logger.info(f"💓 Ping {target['name']} -> OK") # Silence logs to avoid spam
                except Exception as e:
                    logger.debug(f"⚠️ Ping {target['name']} Failed: {e}")
            
            # Aggressive 10s Interval per user request
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(start_heartbeat_hub())
