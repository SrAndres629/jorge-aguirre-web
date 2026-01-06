# =================================================================
# PAGES.PY - Rutas de páginas HTML
# Jorge Aguirre Flores Web
# =================================================================
import time
from fastapi import APIRouter, Request, Response, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.database import save_visitor, get_visitor_fbclid
from app.tracking import generate_external_id, generate_fbc, track_pageview
from app.services import SERVICES_CONFIG, CONTACT_CONFIG

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.head("/", response_class=HTMLResponse)
async def head_root():
    """HEAD response for UptimeRobot (sin tracking)"""
    return Response(status_code=200)


@router.get("/", response_class=HTMLResponse)
async def read_root(
    request: Request, 
    response: Response, 
    background_tasks: BackgroundTasks
):
    """
    PÁGINA DE INICIO
    - Captura fbclid de Meta Ads
    - Envía PageView a CAPI
    - Persiste visitante en PostgreSQL
    """
    event_id = str(int(time.time() * 1000))
    
    # Datos del cliente
    client_ip = request.client.host
    user_agent = request.headers.get('user-agent', '')
    current_url = str(request.url)
    
    # Capturar fbclid de la URL (tráfico de Meta Ads)
    fbclid = request.query_params.get('fbclid')
    
    # Generar external_id único para el visitante
    external_id = generate_external_id(client_ip, user_agent)
    
    # Si no hay fbclid en URL, intentar recuperar de la DB
    if not fbclid:
        fbclid = get_visitor_fbclid(external_id)
    
    # Si hay fbclid, guardar cookie y persistir en DB
    if fbclid:
        fbc_value = generate_fbc(fbclid)
        response.set_cookie(
            key="_fbc", 
            value=fbc_value, 
            max_age=90*24*60*60,  # 90 días
            httponly=True, 
            samesite="lax"
        )
        # Guardar en DB (task en background)
        background_tasks.add_task(
            save_visitor, 
            external_id, 
            fbclid, 
            client_ip, 
            user_agent, 
            "pageview"
        )
    
    # Enviar PageView a Meta CAPI (task en background)
    background_tasks.add_task(
        track_pageview,
        current_url,
        client_ip,
        user_agent,
        event_id,
        fbclid,
        external_id
    )
    
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "pixel_id": settings.META_PIXEL_ID,
        "pageview_event_id": event_id,
        "external_id": external_id,
        "fbclid": fbclid or "",
        "services": SERVICES_CONFIG,
        "contact": CONTACT_CONFIG
    })
