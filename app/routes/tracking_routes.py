# =================================================================
# TRACKING_ROUTES.PY - Endpoints de tracking para Meta
# Jorge Aguirre Flores Web
# =================================================================
import time
from fastapi import APIRouter, Request, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse

from app.models import LeadTrackRequest, ViewContentRequest, TrackResponse, SliderTrackRequest
from app.database import save_visitor, get_visitor_fbclid
from app.tracking import (
    generate_external_id, 
    extract_fbclid_from_fbc,
    track_lead,
    track_viewcontent,
    track_slider_interaction
)

router = APIRouter(prefix="/track", tags=["Tracking"])


@router.post("-lead", response_model=TrackResponse)
async def track_lead_endpoint(
    request: Request, 
    data: LeadTrackRequest,
    background_tasks: BackgroundTasks
):
    """
    TRACKING DE LEAD
    Envía evento Lead a Meta CAPI cuando usuario hace clic en WhatsApp
    """
    try:
        client_ip = request.client.host
        user_agent = request.headers.get('user-agent', '')
        external_id = generate_external_id(client_ip, user_agent)
        
        # Recuperar fbclid de cookie o base de datos
        fbclid = None
        fbc_cookie = request.cookies.get("_fbc")
        if fbc_cookie:
            fbclid = extract_fbclid_from_fbc(fbc_cookie)
        
        if not fbclid:
            fbclid = get_visitor_fbclid(external_id)
        
        # Guardar conversión en DB
        background_tasks.add_task(
            save_visitor, 
            external_id, 
            fbclid, 
            client_ip, 
            user_agent, 
            f"lead_{data.source}"
        )
        
        # Enviar Lead a Meta CAPI
        background_tasks.add_task(
            track_lead,
            str(request.url),
            client_ip,
            user_agent,
            data.event_id,
            data.source,
            fbclid,
            external_id,
            data.service_data
        )
        
        return TrackResponse(status="success", event_id=data.event_id)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("-viewcontent", response_model=TrackResponse)
async def track_viewcontent_endpoint(
    request: Request, 
    data: ViewContentRequest,
    background_tasks: BackgroundTasks
):
    """
    TRACKING DE VIEWCONTENT
    Envía evento ViewContent para retargeting de servicios específicos
    """
    try:
        # Usar event_id del frontend si existe (mejor deduplicación), si no generar uno
        event_id = data.event_id if data.event_id else f"vc_{int(time.time() * 1000)}"
        
        client_ip = request.client.host
        user_agent = request.headers.get('user-agent', '')
        external_id = generate_external_id(client_ip, user_agent)
        
        # Recuperar fbclid wait...
        fbclid = None
        fbc_cookie = request.cookies.get("_fbc")
        if fbc_cookie:
            fbclid = extract_fbclid_from_fbc(fbc_cookie)
        
        if not fbclid:
            fbclid = get_visitor_fbclid(external_id)
        
        # Enviar ViewContent a Meta CAPI
        background_tasks.add_task(
            track_viewcontent,
            str(request.url),
            client_ip,
            user_agent,
            event_id,
            data.service,
            data.category,
            data.price or 0,
            fbclid,
            external_id
        )
        
        return TrackResponse(
            status="success", 
            event_id=event_id,
            category=data.category
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("-slider", response_model=TrackResponse)
async def track_slider_endpoint(
    request: Request,
    data: SliderTrackRequest,
    background_tasks: BackgroundTasks
):
    """
    TRACKING DE SLIDER INTERACTION
    Envía evento SliderInteraction cuando usuario interactúa con antes/después
    """
    try:
        client_ip = request.client.host
        user_agent = request.headers.get('user-agent', '')
        external_id = generate_external_id(client_ip, user_agent)
        
        # Recuperar fbclid wait...
        fbclid = None
        fbc_cookie = request.cookies.get("_fbc")
        if fbc_cookie:
            fbclid = extract_fbclid_from_fbc(fbc_cookie)
        
        if not fbclid:
            fbclid = get_visitor_fbclid(external_id)
        
        # Enviar a Meta CAPI
        background_tasks.add_task(
            track_slider_interaction,
            str(request.url),
            client_ip,
            user_agent,
            data.event_id,
            data.service_name,
            data.service_id,
            data.interaction_type,
            fbclid,
            external_id
        )
        
        return TrackResponse(status="success", event_id=data.event_id)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
