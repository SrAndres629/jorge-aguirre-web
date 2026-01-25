# =================================================================
# PAGES.PY - Rutas de páginas HTML
# Jorge Aguirre Flores Web
# =================================================================
import time
from fastapi import APIRouter, Request, Response, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.database import get_visitor_fbclid
from app.tracking import generate_external_id, generate_fbc
from app.tasks import save_visitor_task, send_meta_event_task
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
    response: Response
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
        try:
            fbclid = get_visitor_fbclid(external_id)
        except Exception as e:
            print(f"⚠️ DB Warning (Non-critical): Could not retrieve visitor fbclid: {e}")
            fbclid = None
    
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
        # Guardar en DB (Celery)
        try:
            save_visitor_task.delay(
                external_id=external_id, 
                fbclid=fbclid or "", 
                client_ip=client_ip, 
                user_agent=user_agent, 
                source="pageview",
                utm_data={}
            )
        except Exception as e:
            # Fallback silencioso (no romper la página por logs)
            print(f"⚠️ Error queuing save_visitor: {e}")
    
    # Enviar PageView a Meta CAPI (Celery)
    # Enviar PageView a Meta CAPI (Celery)
    try:
        send_meta_event_task.delay(
            event_name="PageView",
            event_source_url=current_url,
            client_ip=client_ip,
            user_agent=user_agent,
            event_id=event_id,
            fbclid=fbclid,
            external_id=external_id,
            custom_data={}
        )
    except Exception as e:
        print(f"⚠️ Error queuing Meta Event: {e}")
    
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "pixel_id": settings.META_PIXEL_ID,
        "pageview_event_id": event_id,
        "external_id": external_id,
        "fbclid": fbclid or "",
        "services": SERVICES_CONFIG,
        "contact": CONTACT_CONFIG
    })
