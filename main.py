from fastapi import FastAPI, Request, BackgroundTasks, Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.gzip import GZipMiddleware
import requests
import time
import uvicorn
import hashlib
import uuid

# =================================================================
# CONFIGURACIÓN DEL SISTEMA
# =================================================================
app = FastAPI()

# GZip para carga 5x más rápida en móviles
app.add_middleware(GZipMiddleware, minimum_size=1000)

# IDs de Marketing (Meta Ads)
META_PIXEL_ID = "1412977383680793"
META_ACCESS_TOKEN = "EAAmeW8lDnZAQBQJ61ZC4CCfcNFZBZAQuFBJE06SOZB1AvAexCyUVY3ajvW9u46dvMoYvFMSudqhdYNW4A2PQicr0tcUZBG0itr9ZBUZAuzq7eC83avJT9ox75W5WrncNheJ928IZAo4BxB403x8eeckpdYU8dgu84pHxZC0lEVssgLWWE1Xm30JZCuQbKKkoZB2dkgZDZD"

# Usar la API más reciente de Meta (v21.0)
META_API_VERSION = "v21.0"

# Test Event Code (Activar en Administrador de Eventos para pruebas)
# Descomenta esta línea y agrega tu código de prueba
# TEST_EVENT_CODE = "TEST12345"
TEST_EVENT_CODE = None

# Configuración de archivos
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# =================================================================
# FUNCIONES DE HASHING (Requerido por Meta para datos de usuario)
# =================================================================
def hash_data(value: str) -> str:
    """Hash SHA-256 en minúsculas para datos de usuario (requerido por Meta)"""
    if not value:
        return None
    return hashlib.sha256(value.lower().strip().encode('utf-8')).hexdigest()

def generate_external_id(ip: str, user_agent: str) -> str:
    """Genera un external_id único basado en IP + User Agent (fingerprint ligero)"""
    combined = f"{ip}_{user_agent}"
    return hashlib.sha256(combined.encode('utf-8')).hexdigest()[:32]

def generate_fbc(fbclid: str) -> str:
    """Genera el parámetro fbc a partir del fbclid de la URL"""
    if not fbclid:
        return None
    timestamp = int(time.time())
    return f"fb.1.{timestamp}.{fbclid}"

# =================================================================
# LÓGICA DE TRACKING (CONVERSIONS API - CAPI) - OPTIMIZADA
# =================================================================
def send_to_meta_capi(
    event_name: str, 
    event_source_url: str, 
    client_ip: str, 
    user_agent: str, 
    event_id: str,
    fbclid: str = None,
    external_id: str = None,
    custom_data: dict = None
):
    """
    ENVÍO AL SERVIDOR DE META - OPTIMIZADO PARA MÁXIMO EMQ
    Event Match Quality Score determina qué tan bien Meta puede atribuir las conversiones.
    """
    url = f"https://graph.facebook.com/{META_API_VERSION}/{META_PIXEL_ID}/events"
    
    # Construir user_data con todos los parámetros posibles para máximo EMQ
    user_data = {
        "client_ip_address": client_ip,
        "client_user_agent": user_agent,
    }
    
    # Agregar external_id (mejora EMQ significativamente)
    if external_id:
        user_data["external_id"] = hash_data(external_id)
    
    # Agregar fbc (click ID de Facebook - MUY importante para atribución)
    if fbclid:
        user_data["fbc"] = generate_fbc(fbclid)
    
    # Construir evento
    event_data = {
        "event_name": event_name,
        "event_time": int(time.time()),
        "event_id": event_id,
        "action_source": "website",
        "event_source_url": event_source_url,
        "user_data": user_data
    }
    
    # Agregar custom_data si existe
    if custom_data:
        event_data["custom_data"] = custom_data
    
    payload = {
        "data": [event_data],
        "access_token": META_ACCESS_TOKEN
    }
    
    # Agregar test_event_code si está configurado (para pruebas)
    if TEST_EVENT_CODE:
        payload["test_event_code"] = TEST_EVENT_CODE
    
    try:
        response = requests.post(url, json=payload)
        result = response.json()
        print(f"[META CAPI] {event_name} | Status: {response.status_code} | EMQ params: IP, UA, external_id={bool(external_id)}, fbc={bool(fbclid)}")
        if response.status_code != 200:
            print(f"[META CAPI ERROR] Response: {result}")
    except Exception as e:
        print(f"[ERROR CAPI]: {e}")

# =================================================================
# RUTAS DE LA PÁGINA
# =================================================================

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, response: Response, background_tasks: BackgroundTasks):
    """
    PÁGINA DE INICIO - CON CAPTURA DE FBCLID
    """
    # ID único para deduplicación
    event_id = str(int(time.time() * 1000))
    
    # Datos del visitante
    client_ip = request.client.host
    user_agent = request.headers.get('user-agent', '')
    current_url = str(request.url)
    
    # Capturar fbclid de la URL (muy importante para atribución de ads)
    fbclid = request.query_params.get('fbclid')
    
    # Generar external_id único para este visitante
    external_id = generate_external_id(client_ip, user_agent)
    
    # Si hay fbclid, guardarlo en cookie para futuras conversiones
    if fbclid:
        fbc_value = generate_fbc(fbclid)
        response.set_cookie(key="_fbc", value=fbc_value, max_age=90*24*60*60, httponly=True, samesite="lax")
    
    # Enviar PageView a Meta CAPI (en background)
    background_tasks.add_task(
        send_to_meta_capi, 
        "PageView", 
        current_url, 
        client_ip, 
        user_agent, 
        event_id,
        fbclid,
        external_id
    )
    
    # Renderizar página
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "pixel_id": META_PIXEL_ID,
        "pageview_event_id": event_id,
        "external_id": external_id,
        "fbclid": fbclid or ""
    })

@app.post("/track-lead")
async def track_lead(request: Request, background_tasks: BackgroundTasks):
    """
    TRACKING DE LEAD - OPTIMIZADO PARA MÁXIMO EMQ
    """
    data = await request.json()
    
    # Recuperar fbclid de la cookie si existe
    fbclid = None
    fbc_cookie = request.cookies.get("_fbc")
    if fbc_cookie and fbc_cookie.startswith("fb.1."):
        # Extraer el fbclid de la cookie fbc
        parts = fbc_cookie.split(".")
        if len(parts) >= 4:
            fbclid = parts[3]
    
    # Generar external_id
    external_id = generate_external_id(request.client.host, request.headers.get('user-agent', ''))
    
    # Custom data para el Lead
    custom_data = {
        "content_name": data.get("source", "WhatsApp Lead"),
        "content_category": "lead",
        "lead_source": data.get("source")
    }
    
    background_tasks.add_task(
        send_to_meta_capi, 
        "Lead", 
        str(request.url), 
        request.client.host, 
        request.headers.get('user-agent', ''),
        data.get("event_id"),
        fbclid,
        external_id,
        custom_data
    )
    return {"status": "success"}

@app.post("/track-viewcontent")
async def track_viewcontent(request: Request, background_tasks: BackgroundTasks):
    """
    TRACKING DE VIEWCONTENT - PARA RETARGETING SEGMENTADO
    """
    data = await request.json()
    event_id = f"vc_{int(time.time() * 1000)}"
    
    # Recuperar fbclid de la cookie
    fbclid = None
    fbc_cookie = request.cookies.get("_fbc")
    if fbc_cookie and fbc_cookie.startswith("fb.1."):
        parts = fbc_cookie.split(".")
        if len(parts) >= 4:
            fbclid = parts[3]
    
    external_id = generate_external_id(request.client.host, request.headers.get('user-agent', ''))
    
    custom_data = {
        "content_name": data.get("service"),
        "content_category": data.get("category"),
        "content_type": "service",
        "value": data.get("price", 0),
        "currency": "USD"
    }
    
    background_tasks.add_task(
        send_to_meta_capi,
        "ViewContent",
        str(request.url),
        request.client.host,
        request.headers.get('user-agent', ''),
        event_id,
        fbclid,
        external_id,
        custom_data
    )
    
    return {"status": "success", "category": data.get("category")}

# ARRANQUE DEL SISTEMA
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
