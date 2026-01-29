import logging
import os
import traceback
from contextlib import asynccontextmanager
from typing import Optional, List, Union, Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.chat_routes import router as chat_router
from app.routes.tracking_routes import router as tracking_router
from app.config import settings

app = FastAPI(
    title="Natalia AI Brain",
    description="Dual-Core Intelligence System for Jorge Aguirre Flores",
    version="3.1.0"
)

# --- SENIOR HEALTH PROTOCOL ---
@app.get("/health")
async def health_check():
    """Endpoint for Render keep-alive and institutional monitoring"""
    from app.config import settings
    return {
        "status": "online",
        "version": "3.1.0",
        "instance": settings.EVOLUTION_INSTANCE,
        "engine": "Dual-Core V3"
    }
# ------------------------------

# Configuración de CORS

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Include Routers
app.include_router(chat_router, prefix="/api", tags=["Chat"])
app.include_router(tracking_router, tags=["Tracking"])

from app.routes.admin_routes import router as admin_router
app.include_router(admin_router, tags=["Admin"])

# --- WEBHOOK ALIAS (Fix for 404) ---
from fastapi import BackgroundTasks, Request
@app.post("/webhook/evolution")
async def root_webhook_alias(request: Request, background_tasks: BackgroundTasks):
    """
    Alias for /api/webhook/evolution to support legacy Evolution config.
    """
    from app.chat_routes import handle_evolution_webhook
    return await handle_evolution_webhook(request, background_tasks)
# -----------------------------------


from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request


# Better template path resolution
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

@app.get("/api/health")
def health():
    return {"status": "Natalia is online and thinking."}

from fastapi.responses import RedirectResponse

@app.get("/")
async def root(request: Request):
    """
    Redirección Inteligente (Protocolo Antigravity):
    - Si el servicio es 'natalia-brain', redirige al dominio oficial para proteger la API.
    - Si el servicio es la web oficial o desarrollo local, sirve la página.
    """
    service_name = os.getenv("RENDER_SERVICE_NAME", "").lower()
    host = request.headers.get("host", "").lower()
    
    # 1. Si soy explícitamente el Cerebro o estoy en la URL técnica de Render, redirijo.
    is_brain_service = "natalia-brain" in service_name
    is_technical_url = "onrender.com" in host
    
    if (is_brain_service or is_technical_url) and "jorgeaguirreflores.com" not in host:
        return RedirectResponse(url="https://jorgeaguirreflores.com", status_code=301)
    
    # 2. En cualquier otro caso (Web oficial o Local), servimos la web.
    try:
        contact = {"maps_url": "#", "address": "Santa Cruz de la Sierra, Bolivia"}
        return templates.TemplateResponse("index.html", {
            "request": request, 
            "service": "Natalia AI",
            "contact": contact,
            "services": [],
            "pixel_id": settings.META_PIXEL_ID,
            "pageview_event_id": "",
            "external_id": ""
        })
    except Exception as e:
        logger.error(f"Template Error: {e}")
        return HTMLResponse("Natalia Brain is Online. (Web Template not found)")


# ==========================================
# DUAL-CORE KEEP-ALIVE: Heartbeat for Evolution
# ==========================================
import asyncio
import httpx
import os
import logging

logger = logging.getLogger("NataliaCore")
EVOLUTION_URL = settings.EVOLUTION_API_URL

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
    # 1. Start Triple-Node Heartbeat (Keep-Alive)
    from app.heartbeat import start_heartbeat_hub
    asyncio.create_task(start_heartbeat_hub())

    # 2. Start Auto-Healing Watchdog (Antigravity SRE)
    from app.watchdog import start_watchdog
    asyncio.create_task(start_watchdog())
    
    # 3. Senior Protocol: Admin initialization message (SILENCED to avoid restart spam)
    # from app.evolution import evolution_service
    # from app.natalia import ADMIN_PHONE
    
    # logger.info(f"🚀 Natalia initializing. Sending heartbeat to Admin: {ADMIN_PHONE}")
    
    # startup_msg = (
    #     "🧠 *NATALIA CORE V3.0 ACTIVADA*\n\n"
    #     "He despertado y mis sistemas neuronales están en línea. 🚀\n"
    #     "Estoy monitoreando la conexión con Evolution y lista para recibir mensajes."
    # )
    
    # Send via background task to not block startup
    # asyncio.create_task(evolution_service.send_text(ADMIN_PHONE, startup_msg))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
