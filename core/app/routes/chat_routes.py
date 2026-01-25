
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
import httpx
import logging
from app.natalia import natalia
from app.config import settings

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
                send_whatsapp_legacy, 
                phone=msg.phone, 
                text=result["reply"]
            )
            
        return {"status": "processed", "action": result.get("action")}
        
    except Exception as e:
        logger.error(f"❌ Chat Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def send_whatsapp_legacy(phone: str, text: str):
    """
    Envía mensaje usando la Evolution API.
    Nota: Usamos 'JorgeMain' como instancia hardcodeada por ahora.
    """
    url = f"{settings.EVOLUTION_API_URL}/message/sendText/JorgeMain"
    headers = {"apikey": settings.EVOLUTION_API_KEY}
    payload = {
        "number": phone,
        "text": text
    }
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            logger.info(f"📤 Reply sent to {phone}")
        except Exception as e:
            logger.error(f"❌ Failed to send reply: {e}")
