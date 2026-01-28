
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
    Recibe el payload raw, extrae el mensaje y lo pasa al Cerebro.
    """
    try:
        body = await request.json()
        
        # Validar tipo de evento
        event_type = body.get("type")
        data = body.get("data", {})
        
        # Solo nos interesan mensajes nuevos (UPSERT)
        if event_type == "MESSAGES_UPSERT":
            message_data = data
            key = message_data.get("key", {})
            from_me = key.get("fromMe", False)
            
            # Ignorar mensajes propios para evitar bucles
            if from_me:
                return {"status": "ignored", "reason": "from_me"}
            
            # Extraer Teléfono (remoteJid)
            remote_jid = key.get("remoteJid", "")
            phone = remote_jid.split("@")[0] if "@" in remote_jid else remote_jid
            
            # Extraer Texto (conversation, extendedTextMessage, etc.)
            message_content = message_data.get("message", {})
            text = (
                message_content.get("conversation") or 
                message_content.get("extendedTextMessage", {}).get("text") or
                message_content.get("imageMessage", {}).get("caption") or
                ""
            )
            
            if not text:
                 return {"status": "ignored", "reason": "no_text"}

            # Extraer Nombre
            push_name = message_data.get("pushName", "Unknown")
            
            # Procesar con Natalia (reutilizando lógica interna)
            logger.info(f"📨 Webhook Evolution recibido de {phone}: {text[:30]}...")
            
            # -- Lógica idéntica a /chat/incoming --
            # Construct dynamic metadata
            meta = {
                "name": push_name,
                "source": "evolution_webhook"
            }

            # Process Logic (Buffered via InboxManager)
            # We don't await the result here because it's processed asynchronously
            await inbox_manager.add_message(
                phone=phone, 
                text=text, 
                meta_data=meta
            )
            
            # We return "queued" instead of "processed"
            return {"status": "queued", "phone": phone}
            
        return {"status": "ignored", "type": event_type}

    except Exception as e:
        logger.error(f"❌ Webhook Error: {e}")
        # Retornamos 200 para que Evolution no reintente infinitamente si es un error lógico nuestro
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
