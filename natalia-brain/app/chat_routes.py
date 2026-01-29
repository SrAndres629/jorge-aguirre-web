
from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
from app.natalia import natalia
from app.inbox_manager import inbox_manager
from app.utils.normalizer import normalize_evolution_payload

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

class EvolutionAdapter:
    """
    Standardized Adapter for Evolution API v2 Webhooks.
    Ensures Idempotency, normalization and safe ingestion.
    """
    @staticmethod
    async def ingest(request: Request) -> Dict[str, Any]:
        try:
            body = await request.json()
            msg = normalize_evolution_payload(body)
            
            if not msg:
                return {"status": "ignored"}
                
            logger.info(f"📨 [GATEWAY] INGEST: {msg.id} | SENDER: {msg.sender} | TYPE: {msg.type}")
            
            # Idempotency / Buffer Logic
            meta = {
                "name": msg.name,
                "source": msg.source,
                "timestamp": msg.timestamp,
                "type": msg.type
            }
            
            await inbox_manager.add_message(
                phone=msg.sender, 
                text=msg.text, 
                meta_data=meta
            )
            
            return {"status": "queued", "phone": msg.sender}
            
        except Exception as e:
            logger.error(f"❌ [GATEWAY] Adapter Error: {e}")
            # Prevent retry loops from webhook provider
            return {"status": "error_logged", "message": "Handled Safe"}

@router.post("/webhook/evolution")
async def handle_evolution_webhook(request: Request, background_tasks: BackgroundTasks):
    # Delegate to Adapter
    return await EvolutionAdapter.ingest(request)

@router.post("/chat/incoming")
async def handle_incoming_chat(msg: IncomingMessage, request: Request, background_tasks: BackgroundTasks):
    try:
        meta = {
            "name": msg.name,
            "profile_pic_url": msg.profile_pic,
            "fbclid": msg.fbclid,
            "fbp": msg.fbp
        }
        if msg.utm_data:
            meta.update(msg.utm_data)

        await inbox_manager.add_message(
            phone=msg.phone, 
            text=msg.text, 
            meta_data=meta
        )
        return {"status": "queued", "action": "buffer_add", "is_new_lead": None}
    except Exception as e:
        logger.error(f"❌ Chat Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class BookingConfirm(BaseModel):
    phone: str
    service_name: str
    value: float = 300.0

@router.post("/admin/confirm-booking")
async def confirm_booking(data: BookingConfirm):
    from app.tasks import track_booking_confirmed_task
    track_booking_confirmed_task.delay(
        phone=data.phone, 
        service_name=data.service_name, 
        value=data.value
    )
    return {"status": "success", "message": "Gold Loop conversion queued"}
