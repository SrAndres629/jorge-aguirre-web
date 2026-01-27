
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.chat_routes import router as chat_router
from app.config import settings

app = FastAPI(title="Natalia AI Core", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)

@app.get("/health")
def health():
    return {"status": "Natalia is online and thinking."}


# ==========================================
# DUAL-CORE KEEP-ALIVE: Heartbeat for Evolution
# ==========================================
import asyncio
import httpx
import os
import logging

logger = logging.getLogger("NataliaCore")
EVOLUTION_URL = os.getenv("EVOLUTION_URL", "https://evolution-whatsapp-zn13.onrender.com")

async def keep_evolution_alive():
    """Background task to ping Evolution API every 45s"""
    async with httpx.AsyncClient() as client:
        while True:
            try:
                # Ping Evolution's root
                await client.get(f"{EVOLUTION_URL}/", timeout=5.0)
                # logger.info(f"💓 Dual-Core Heartbeat: Pinged Evolution at {EVOLUTION_URL}")
            except Exception as e:
                pass
                # logger.warning(f"⚠️ Heartbeat missed Evolution: {e}")
            
            await asyncio.sleep(45)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(keep_evolution_alive())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
