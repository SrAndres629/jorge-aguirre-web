
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any
import httpx
import logging
from app.natalia import natalia
from app.config import settings
from app.evolution import evolution_service

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
    
@router.post("/chat/incoming")
async def handle_incoming_chat(msg: IncomingMessage, background_tasks: BackgroundTasks):
    """
    Endpoint para recibir mensajes de usuarios (via n8n o Evolution Webhook).
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

        # Process Logic
        result = natalia.process_message(
            phone=msg.phone, 
            text=msg.text, 
            meta_data=meta
        )
        
        # Execute Action (Reply)
        if result.get("action") == "send_whatsapp":
            # Send via Evolution API
            # We run this in background to return 200 OK fast
            background_tasks.add_task(
                evolution_service.send_text, 
                phone=msg.phone, 
                text=result["reply"]
            )
            
        return {"status": "processed", "action": result.get("action")}
        
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
