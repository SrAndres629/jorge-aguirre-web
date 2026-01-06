from fastapi import APIRouter, Request, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any
import time
import os
import logging

# Configurar logger
logger = logging.getLogger("tracking")
logger.setLevel(logging.INFO)

router = APIRouter()

# Meta CAPI Configuration (Environment Variables)
PIXEL_ID = os.getenv("META_PIXEL_ID", "123456789")
ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN", "EAA...")
TEST_EVENT_CODE = os.getenv("META_TEST_EVENT_CODE")

from app.tracking import send_event, send_n8n_webhook
from app.database import save_visitor, upsert_contact

class TrackingEvent(BaseModel):
    event_name: str
    event_time: int
    event_id: str
    user_data: Dict[str, Any]
    custom_data: Optional[Dict[str, Any]] = None
    event_source_url: str
    action_source: str = "website"

@router.post("/track/event")
async def track_event(event: TrackingEvent, request: Request, background_tasks: BackgroundTasks):
    """
    Recibe eventos del frontend y los envía a CAPI de forma asíncrona.
    """
    return await process_tracking_event(event, request, background_tasks)

async def process_tracking_event(event: TrackingEvent, request: Request, background_tasks: BackgroundTasks):
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "unknown")
    
    # Extract Data
    custom_data = event.custom_data or {}
    logger.info(f"📥 Incoming Event: {event.event_name} | CustomData: {custom_data}")
    fbclid = custom_data.get('fbclid')
    external_id = event.user_data.get('external_id')
    
    # Extract UTMs
    utm_data = {
        'utm_source': custom_data.get('utm_source'),
        'utm_medium': custom_data.get('utm_medium'),
        'utm_campaign': custom_data.get('utm_campaign'),
        'utm_term': custom_data.get('utm_term'),
        'utm_content': custom_data.get('utm_content')
    }
    
    # 1. PERSISTENCE (Anonymous Visitors Table)
    try:
        save_visitor(
            external_id=external_id or "anon",
            fbclid=fbclid,
            ip_address=client_ip,
            user_agent=user_agent,
            source=event.event_name,
            utm_data=utm_data
        )
    except Exception as e:
        logger.error(f"❌ DB Save Error: {e}")

    # 2. LEAD PERSISTENCE (Contacts Table - CRM)
    # If we have a phone number (e.g. from a form or external_id matching system)
    phone = custom_data.get('phone') or event.user_data.get('phone')
    if event.event_name == 'Lead' and phone:
        contact_payload = {
            'phone': phone,
            'name': custom_data.get('name') or event.user_data.get('name'),
            'fbclid': fbclid,
            **utm_data
        }
        background_tasks.add_task(upsert_contact, contact_payload)

    # 3. CAPI (Background)
    background_tasks.add_task(
        send_event,
        event_name=event.event_name,
        event_source_url=event.event_source_url,
        client_ip=client_ip,
        user_agent=user_agent,
        event_id=event.event_id,
        fbclid=fbclid,
        external_id=external_id,
        custom_data=event.custom_data
    )
    
    # 4. ORCHESTRATION (n8n Webhook)
    IMPORTANT_EVENTS = ['Lead', 'Purchase', 'SliderInteraction']
    if event.event_name in IMPORTANT_EVENTS:
        webhook_payload = event.dict()
        webhook_payload['utm_data'] = utm_data
        background_tasks.add_task(send_n8n_webhook, webhook_payload)
    
    return {"status": "queued", "event_id": event.event_id}


