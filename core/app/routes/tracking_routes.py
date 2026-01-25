from fastapi import APIRouter, Request, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import time
from app.config import settings
import logging
from app.models import TrackResponse, LeadCreate, InteractionCreate

# Logger
logger = logging.getLogger(__name__)

# Router
router = APIRouter()

# Meta CAPI Configuration (From Central Settings)
PIXEL_ID = settings.META_PIXEL_ID
ACCESS_TOKEN = settings.META_ACCESS_TOKEN
TEST_EVENT_CODE = settings.TEST_EVENT_CODE

from app.tracking import send_event, send_n8n_webhook
from app.database import save_visitor, upsert_contact_advanced, get_or_create_lead, log_interaction
import app.database as database

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
    from app.tasks import save_visitor_task, upsert_contact_task, send_meta_event_task, send_n8n_webhook_task

    # Enqueue Visitor Save (Non-blocking)
    save_visitor_task.delay(
        external_id=external_id or "anon",
        fbclid=fbclid,
        client_ip=client_ip,
        user_agent=user_agent,
        source=event.event_name,
        utm_data=utm_data
    )

    # 2. LEAD PERSISTENCE (Contacts Table - CRM)
    phone = custom_data.get('phone') or event.user_data.get('phone')
    if event.event_name == 'Lead' and phone:
        contact_payload = {
            'phone': phone,
            'name': custom_data.get('name') or event.user_data.get('name'),
            'fbclid': fbclid,
            'status': 'interested', # Leads from web are interested
            'service_interest': custom_data.get('service_type') or utm_data.get('utm_campaign'),
            **utm_data
        }
        upsert_contact_task.delay(contact_payload)

    # 3. CAPI (Background via Worker)
    send_meta_event_task.delay(
        event_name=event.event_name,
        event_source_url=event.event_source_url,
        client_ip=client_ip,
        user_agent=user_agent,
        event_id=event.event_id,
        fbclid=fbclid,
        fbp=custom_data.get('fbp'), # Pass FBP
        external_id=external_id,
        custom_data=event.custom_data
    )
    
    # 4. ORCHESTRATION (n8n Webhook via Worker)
    IMPORTANT_EVENTS = ['Lead', 'Purchase', 'SliderInteraction']
    if event.event_name in IMPORTANT_EVENTS:
        webhook_payload = event.model_dump() # Pydantic v2 uses model_dump(), previously dict()
        webhook_payload['utm_data'] = utm_data
        send_n8n_webhook_task.delay(webhook_payload)
    
    return {"status": "queued", "event_id": event.event_id}


# =================================================================
# W-003: TRACKING RESCUE ROUTES
# =================================================================

@router.post("/track/lead", response_model=TrackResponse)
async def track_lead_context(request: LeadCreate):
    """
    Endpoint para n8n/webhook.
    Crea o actualiza un Lead vinculado a WhatsApp y Meta.
    """
    try:
        data = {
            "meta_lead_id": request.meta_lead_id,
            "click_id": request.click_id,
            "email": request.email,
            "name": request.name
        }
        if request.extra_data:
            data.update(request.extra_data)

        lead_id = database.get_or_create_lead(request.whatsapp_phone, data)
        
        if lead_id:
             return TrackResponse(status="success", event_id=str(lead_id), category="lead_generated")
        else:
             raise HTTPException(status_code=500, detail="Database Error creating Lead")

    except Exception as e:
        logger.error(f"❌ Error en /track/lead: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/track/interaction", response_model=TrackResponse)
async def track_interaction(request: InteractionCreate):
    """
    Endpoint para registrar mensajes (User/AI).
    """
    try:
        success = database.log_interaction(request.lead_id, request.role, request.content)
        if success:
            return TrackResponse(status="success", event_id=request.lead_id, category="interaction_logged")
        else:
            raise HTTPException(status_code=500, detail="Database Error logging interaction")
    except Exception as e:
        logger.error(f"❌ Error en /track/interaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))
