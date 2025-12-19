from fastapi import FastAPI, Request, BackgroundTasks, Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.gzip import GZipMiddleware
import requests
import time
import uvicorn
import hashlib
import uuid
import sqlite3
import os
from datetime import datetime

# =================================================================
# CONFIGURACIÓN DEL SISTEMA
# =================================================================
app = FastAPI()

# GZip para carga 5x más rápida en móviles
app.add_middleware(GZipMiddleware, minimum_size=1000)

# IDs de Marketing (Meta Ads)
META_PIXEL_ID = "1412977383680793"
META_ACCESS_TOKEN = "EAAmeW8lDnZAQBQJ61ZC4CCfcNFZBZAQuFBJE06SOZB1AvAexCyUVY3ajvW9u46dvMoYvFMSudqhdYNW4A2PQicr0tcUZBG0itr9ZBUZAuzq7eC83avJT9ox75W5WrncNheJ928IZAo4BxB403x8eeckpdYU8dgu84pHxZC0lEVssgLWWE1Xm30JZCuQbKKkoZB2dkgZDZD"

# API de Meta (v21.0)
META_API_VERSION = "v21.0"

# Test Event Code (para pruebas en Administrador de Eventos)
TEST_EVENT_CODE = None

# Configuración de archivos
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Base de datos - usar /tmp en Render (persistente durante la ejecución)
DB_PATH = "/tmp/tracking.db" if os.environ.get("RENDER") else "tracking.db"

# =================================================================
# SQLITE SHADOW DATABASE - Persistencia de Atribución
# =================================================================
def init_db():
    """Inicializa la base de datos SQLite con tabla de visitantes"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS visitors
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      external_id TEXT NOT NULL,
                      fbclid TEXT,
                      ip_address TEXT,
                      user_agent TEXT,
                      source TEXT,
                      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        c.execute('''CREATE INDEX IF NOT EXISTS idx_external_id ON visitors(external_id)''')
        c.execute('''CREATE INDEX IF NOT EXISTS idx_fbclid ON visitors(fbclid)''')
        conn.commit()
        conn.close()
        print(f"[DB] Shadow database initialized at {DB_PATH}")
    except Exception as e:
        print(f"[DB ERROR] Could not initialize: {e}")

def save_visitor(external_id: str, fbclid: str, ip_address: str, user_agent: str, source: str = "pageview"):
    """Guarda un registro de visitante en la shadow database"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                "INSERT INTO visitors (external_id, fbclid, ip_address, user_agent, source) VALUES (?, ?, ?, ?, ?)",
                (external_id, fbclid, ip_address, user_agent[:500], source)  # Limitar user_agent
            )
        print(f"[DB] Visitor saved: fbclid={bool(fbclid)}")
    except Exception as e:
        print(f"[DB ERROR] Could not save visitor: {e}")

def get_visitor_by_external_id(external_id: str):
    """Recupera el fbclid de un visitante por su external_id"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute(
                "SELECT fbclid FROM visitors WHERE external_id = ? AND fbclid IS NOT NULL ORDER BY timestamp DESC LIMIT 1",
                (external_id,)
            )
            row = cursor.fetchone()
            return row[0] if row else None
    except Exception as e:
        print(f"[DB ERROR] Could not retrieve visitor: {e}")
        return None

# Inicializar DB al arrancar
init_db()

# =================================================================
# FUNCIONES DE HASHING (Requerido por Meta)
# =================================================================
def hash_data(value: str) -> str:
    if not value:
        return None
    return hashlib.sha256(value.lower().strip().encode('utf-8')).hexdigest()

def generate_external_id(ip: str, user_agent: str) -> str:
    combined = f"{ip}_{user_agent}"
    return hashlib.sha256(combined.encode('utf-8')).hexdigest()[:32]

def generate_fbc(fbclid: str) -> str:
    if not fbclid:
        return None
    timestamp = int(time.time())
    return f"fb.1.{timestamp}.{fbclid}"

# =================================================================
# LÓGICA DE TRACKING (CONVERSIONS API - CAPI)
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
    url = f"https://graph.facebook.com/{META_API_VERSION}/{META_PIXEL_ID}/events"
    
    user_data = {
        "client_ip_address": client_ip,
        "client_user_agent": user_agent,
    }
    
    if external_id:
        user_data["external_id"] = hash_data(external_id)
    
    if fbclid:
        user_data["fbc"] = generate_fbc(fbclid)
    
    event_data = {
        "event_name": event_name,
        "event_time": int(time.time()),
        "event_id": event_id,
        "action_source": "website",
        "event_source_url": event_source_url,
        "user_data": user_data
    }
    
    if custom_data:
        event_data["custom_data"] = custom_data
    
    payload = {
        "data": [event_data],
        "access_token": META_ACCESS_TOKEN
    }
    
    if TEST_EVENT_CODE:
        payload["test_event_code"] = TEST_EVENT_CODE
    
    try:
        response = requests.post(url, json=payload)
        print(f"[META CAPI] {event_name} | Status: {response.status_code}")
    except Exception as e:
        print(f"[ERROR CAPI]: {e}")

# =================================================================
# ENDPOINTS - KEEP ALIVE (Para UptimeRobot)
# =================================================================
@app.get("/health")
async def health_check():
    """
    HEALTH CHECK - Endpoint para mantener el servidor activo.
    Configura UptimeRobot (gratis) para hacer ping cada 5 minutos.
    """
    return JSONResponse({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Jorge Aguirre Flores Web"
    })

@app.get("/ping")
async def ping():
    """Endpoint simple para keep-alive"""
    return "pong"

# =================================================================
# RUTAS DE LA PÁGINA
# =================================================================
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, response: Response, background_tasks: BackgroundTasks):
    """PÁGINA DE INICIO - Con tracking y persistencia"""
    event_id = str(int(time.time() * 1000))
    
    client_ip = request.client.host
    user_agent = request.headers.get('user-agent', '')
    current_url = str(request.url)
    
    # Capturar fbclid de la URL
    fbclid = request.query_params.get('fbclid')
    
    # Generar external_id único
    external_id = generate_external_id(client_ip, user_agent)
    
    # Si no hay fbclid en URL, buscar en la shadow database
    if not fbclid:
        fbclid = get_visitor_by_external_id(external_id)
        if fbclid:
            print(f"[DB] Recovered fbclid from shadow database")
    
    # Guardar en shadow database si hay fbclid valioso
    if fbclid:
        fbc_value = generate_fbc(fbclid)
        response.set_cookie(key="_fbc", value=fbc_value, max_age=90*24*60*60, httponly=True, samesite="lax")
        # Guardar en DB para atribución futura
        background_tasks.add_task(save_visitor, external_id, fbclid, client_ip, user_agent, "pageview")
    
    # Enviar PageView a Meta CAPI
    background_tasks.add_task(
        send_to_meta_capi, "PageView", current_url, client_ip, user_agent, event_id, fbclid, external_id
    )
    
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "pixel_id": META_PIXEL_ID,
        "pageview_event_id": event_id,
        "external_id": external_id,
        "fbclid": fbclid or ""
    })

@app.post("/track-lead")
async def track_lead(request: Request, background_tasks: BackgroundTasks):
    """TRACKING DE LEAD - Con recuperación de fbclid"""
    data = await request.json()
    
    client_ip = request.client.host
    user_agent = request.headers.get('user-agent', '')
    external_id = generate_external_id(client_ip, user_agent)
    
    # Recuperar fbclid de cookie o shadow database
    fbclid = None
    fbc_cookie = request.cookies.get("_fbc")
    if fbc_cookie and fbc_cookie.startswith("fb.1."):
        parts = fbc_cookie.split(".")
        if len(parts) >= 4:
            fbclid = parts[3]
    
    # Si no hay en cookie, buscar en DB
    if not fbclid:
        fbclid = get_visitor_by_external_id(external_id)
    
    # Guardar conversión en DB
    background_tasks.add_task(save_visitor, external_id, fbclid, client_ip, user_agent, f"lead_{data.get('source')}")
    
    custom_data = {
        "content_name": data.get("source", "WhatsApp Lead"),
        "content_category": "lead",
        "lead_source": data.get("source")
    }
    
    background_tasks.add_task(
        send_to_meta_capi, "Lead", str(request.url), client_ip, user_agent,
        data.get("event_id"), fbclid, external_id, custom_data
    )
    return {"status": "success"}

@app.post("/track-viewcontent")
async def track_viewcontent(request: Request, background_tasks: BackgroundTasks):
    """TRACKING DE VIEWCONTENT - Para retargeting"""
    data = await request.json()
    event_id = f"vc_{int(time.time() * 1000)}"
    
    client_ip = request.client.host
    user_agent = request.headers.get('user-agent', '')
    external_id = generate_external_id(client_ip, user_agent)
    
    # Recuperar fbclid
    fbclid = None
    fbc_cookie = request.cookies.get("_fbc")
    if fbc_cookie and fbc_cookie.startswith("fb.1."):
        parts = fbc_cookie.split(".")
        if len(parts) >= 4:
            fbclid = parts[3]
    if not fbclid:
        fbclid = get_visitor_by_external_id(external_id)
    
    custom_data = {
        "content_name": data.get("service"),
        "content_category": data.get("category"),
        "content_type": "service",
        "value": data.get("price", 0),
        "currency": "USD"
    }
    
    background_tasks.add_task(
        send_to_meta_capi, "ViewContent", str(request.url), client_ip, user_agent,
        event_id, fbclid, external_id, custom_data
    )
    
    return {"status": "success", "category": data.get("category")}

# =================================================================
# ARRANQUE DEL SISTEMA
# =================================================================
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
