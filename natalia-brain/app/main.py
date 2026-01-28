import logging
import os
import traceback
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.chat_routes import router as chat_router
from app.routes.tracking_routes import router as tracking_router
from app.config import settings

app = FastAPI(title="Natalia AI Core", version="2.0.0")

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

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    try:
        # Mock data for template compatibility (Protocol Phase 1 Stability)
        contact = {
            "maps_url": "#",
            "address": "Santa Cruz de la Sierra, Bolivia"
        }
        services = [] # Fallback
        
        return templates.TemplateResponse("index.html", {
            "request": request, 
            "service": "Natalia Brain V2",
            "contact": contact,
            "services": services,
            "pixel_id": "",
            "pageview_event_id": "",
            "external_id": ""
        })
    except Exception as e:
        import traceback
        return HTMLResponse(content=f"<h1>500 Internal Server Error (Template Crash)</h1><pre>{traceback.format_exc()}</pre>", status_code=500)


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
    # 1. Start Keep-Alive Heartbeat
    asyncio.create_task(keep_evolution_alive())
    
    # 2. Senior Protocol: Admin initialization message (SILENCED to avoid restart spam)
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
