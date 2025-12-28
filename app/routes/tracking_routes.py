from fastapi import APIRouter, Request, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any
import time
import os
import httpx
import logging

# Configurar logger
logger = logging.getLogger("tracking")
logger.setLevel(logging.INFO)

router = APIRouter()

# Meta CAPI Configuration (Environment Variables)
PIXEL_ID = os.getenv("META_PIXEL_ID", "123456789")
ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN", "EAA...")
TEST_EVENT_CODE = os.getenv("META_TEST_EVENT_CODE")

class TrackingEvent(BaseModel):
    event_name: str
    event_time: int
    event_id: str
    user_data: Dict[str, Any]
    custom_data: Optional[Dict[str, Any]] = None
    event_source_url: str
    action_source: str = "website"

async def send_to_capi(event: TrackingEvent, client_ip: str, user_agent: str):
    """
    Simula (o ejecuta) el envío del evento a Meta Conversions API.
    En un entorno real, descomentar la petición HTTP.
    """
    
    # Preparar payload para Meta
    payload = {
        "data": [
            {
                "event_name": event.event_name,
                "event_time": event.event_time,
                "event_id": event.event_id,
                "event_source_url": event.event_source_url,
                "action_source": event.action_source,
                "user_data": {
                    "client_ip_address": client_ip,
                    "client_user_agent": user_agent,
                    # Hashed PII should be passed here (email, phone) if available
                    **event.user_data
                },
                "custom_data": event.custom_data
            }
        ]
    }
    
    if TEST_EVENT_CODE:
        payload["test_event_code"] = TEST_EVENT_CODE

    url = f"https://graph.facebook.com/v18.0/{PIXEL_ID}/events?access_token={ACCESS_TOKEN}"
    
    try:
        # async with httpx.AsyncClient() as client:
        #     resp = await client.post(url, json=payload)
        #     resp.raise_for_status()
        #     logger.info(f"CAPI Success: {resp.json()}")
        
        # Simulación de éxito para evitar errores sin token real
        logger.info(f"CAPI Simulated Send: {event.event_name} | ID: {event.event_id}")
        
    except Exception as e:
        logger.error(f"CAPI Error: {str(e)}")

@router.post("/track/event")
async def track_event(event: TrackingEvent, request: Request, background_tasks: BackgroundTasks):
    """
    Endpoint paralizado para recibir eventos del frontend y enviarlos a CAPI
    de forma asíncrona (Fire & Forget).
    """
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "unknown")
    
    # Delegar envío a background para no bloquear respuesta al cliente
    background_tasks.add_task(send_to_capi, event, client_ip, user_agent)
    
    return {"status": "queued", "event_id": event.event_id}
