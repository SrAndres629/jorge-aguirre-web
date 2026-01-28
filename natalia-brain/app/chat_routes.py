
from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from pydantic import BaseModel
from typing import Optional, Dict, Any
import httpx
import logging
import time
from app.natalia import natalia
from app.inbox_manager import inbox_manager
from app.config import settings
from app.evolution import evolution_service
from app.routes.tracking_routes import bg_send_meta_event

router = APIRouter()
logger = logging.getLogger("ChatRoutes")

class IncomingMessage(BaseModel):
    phone: str
    text: str
    name: str = "Unknown"
    profile_pic: Optional[str] = None
    fbclid: Optional[str] = None
    fbp: Optional[str] = None
    utm_data: Optional[Dict[str, Any]] = None
    

@router.post("/webhook/evolution")
async def handle_evolution_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Adapter nativo para Evolution API v2.
    Implementa Protocolo Surjectivo f: W -> G
    """
    try:
        body = await request.json()
        
        # 1. Normalize (Safe Ingestion)
        # Avoids logic errors by delegating parsing to pure function
        from app.utils.normalizer import normalize_evolution_payload
        
        msg = normalize_evolution_payload(body)
        
        if not msg:
            # Valid ignored message (echo or non-text)
            return {"status": "ignored"}
            
        # 2. Structured Logging (Trazabilidad)
        logger.info(f"📨 [GATEWAY] INGEST: {msg.id} | PHONE: {msg.phone} | NAME: {msg.name}")

        # 3. Buffer Logic (Inject into Brain)
        meta = {
            "name": msg.name,
            "source": msg.source,
            "timestamp": msg.timestamp
        }
        
        # Pass to Inbox Manager (asynchronous processing)
        await inbox_manager.add_message(
            phone=msg.phone, 
            text=msg.text, 
            meta_data=meta
        )
        
        return {"status": "queued", "phone": msg.phone}

    except Exception as e:
        logger.error(f"❌ [GATEWAY] CRITICAL: {e}")
        return {"status": "error", "message": str(e)}

@router.post("/chat/incoming")
async def handle_incoming_chat(msg: IncomingMessage, request: Request, background_tasks: BackgroundTasks):
    """
    Endpoint para recibir mensajes de usuarios (via n8n o Evolution Webhook).
    Si es un nuevo lead, dispara evento Lead a Meta CAPI.
    """
    try:
        # Construct dynamic metadata
        meta = {
            "name": msg.name,
            "profile_pic_url": msg.profile_pic,
            "fbclid": msg.fbclid,
            "fbp": msg.fbp
        }
        if msg.utm_data:
            meta.update(msg.utm_data)

        # Process Logic (Buffered via InboxManager)
        await inbox_manager.add_message(
            phone=msg.phone, 
            text=msg.text, 
            meta_data=meta
        )
        
        # NOTE: logic regarding Meta CAPI signal injection is now tricky because 
        # we don't have the result immediately. 
        # Ideally, we should move the Meta CAPI trigger to the InboxManager or NataliaBrain class
        # after processing is complete.
        # For now, we will assume leads are tracked inside natalia.process_message -> log_interaction
        
        return {"status": "queued", "action": "buffer_add", "is_new_lead": None}
        
    except Exception as e:
        logger.error(f"❌ Chat Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Removed send_whatsapp_legacy as it is now handled by evolution_service.py

# =================================================================
# PILLAR 2: THE GOLD FEEDBACK LOOP
# =================================================================

class BookingConfirm(BaseModel):
    phone: str
    service_name: str
    value: float = 300.0

@router.post("/admin/confirm-booking")
async def confirm_booking(data: BookingConfirm):
    """
    Endpoint manual para Jorge. Al confirmar una cita, 
    se notifica a Meta para cerrar el círculo de optimización.
    """
    from app.tasks import track_booking_confirmed_task
    track_booking_confirmed_task.delay(
        phone=data.phone, 
        service_name=data.service_name, 
        value=data.value
    )
    return {"status": "success", "message": "Gold Loop conversion queued"}
