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

from app.tracking import send_event

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

# LEGACY ENDPOINTS (Prevents 404 from cached scripts)
@router.post("/track-lead")
async def track_lead_legacy(data: Dict[str, Any], request: Request, background_tasks: BackgroundTasks):
    event = TrackingEvent(
        event_name="Lead",
        event_time=int(time.time()),
        event_id=f"legacy_lead_{int(time.time())}",
        user_data={"external_id": data.get("external_id", "")},
        custom_data=data,
        event_source_url=str(request.url)
    )
    return await process_tracking_event(event, request, background_tasks)

@router.post("/track-viewcontent")
async def track_vc_legacy(data: Dict[str, Any], request: Request, background_tasks: BackgroundTasks):
    event = TrackingEvent(
        event_name="ViewContent",
        event_time=int(time.time()),
        event_id=f"legacy_vc_{int(time.time())}",
        user_data={"external_id": data.get("external_id", "")},
        custom_data=data,
        event_source_url=str(request.url)
    )
    return await process_tracking_event(event, request, background_tasks)

@router.post("/track-slider")
async def track_slider_legacy(data: Dict[str, Any], request: Request, background_tasks: BackgroundTasks):
    event = TrackingEvent(
        event_name="SliderInteraction",
        event_time=int(time.time()),
        event_id=f"legacy_slider_{int(time.time())}",
        user_data={"external_id": data.get("external_id", "")},
        custom_data=data,
        event_source_url=str(request.url)
    )
    return await process_tracking_event(event, request, background_tasks)

async def process_tracking_event(event: TrackingEvent, request: Request, background_tasks: BackgroundTasks):
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "unknown")
    
    fbclid = None
    if event.custom_data:
        fbclid = event.custom_data.get('fbclid')
    
    external_id = event.user_data.get('external_id')
    
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
    
    return {"status": "queued", "event_id": event.event_id}

