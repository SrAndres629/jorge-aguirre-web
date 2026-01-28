
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


from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/api/health")
def health():
    return {"status": "Natalia is online and thinking."}

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "service": "Natalia Brain V2"})


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
    # 1. Start Keep-Alive Heartbeat
    asyncio.create_task(keep_evolution_alive())
    
    # 2. Senior Protocol: Admin initialization message
    from app.evolution import evolution_service
    from app.natalia import ADMIN_PHONE
    
    logger.info(f"🚀 Natalia initializing. Sending heartbeat to Admin: {ADMIN_PHONE}")
    
    startup_msg = (
        "🧠 *NATALIA CORE V3.0 ACTIVADA*\n\n"
        "He despertado y mis sistemas neuronales están en línea. 🚀\n"
        "Estoy monitoreando la conexión con Evolution y lista para recibir mensajes."
    )
    
    # Send via background task to not block startup
    asyncio.create_task(evolution_service.send_text(ADMIN_PHONE, startup_msg))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
