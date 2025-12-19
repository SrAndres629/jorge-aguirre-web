from fastapi import FastAPI, Request, BackgroundTasks, Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.gzip import GZipMiddleware
import requests
import time
import uvicorn
import hashlib
import os
from datetime import datetime
import psycopg2

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

# Test Event Code (para pruebas)
TEST_EVENT_CODE = None

# Configuración de archivos
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# =================================================================
# POSTGRESQL (SUPABASE) - Base de Datos Persistente
# =================================================================
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    """Obtiene conexión a PostgreSQL (Supabase)"""
    if not DATABASE_URL:
        return None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"❌ Error conectando a DB: {e}")
        return None

def init_db():
    """Inicializa la tabla visitors en PostgreSQL"""
    conn = get_db_connection()
    if not conn:
        print("⚠️ No hay DATABASE_URL configurada. Saltando inicialización de DB.")
        return
    
    try:
        cur = conn.cursor()
        # Sintaxis PostgreSQL con SERIAL
        cur.execute('''
            CREATE TABLE IF NOT EXISTS visitors (
                id SERIAL PRIMARY KEY,
                external_id TEXT NOT NULL,
                fbclid TEXT,
                ip_address TEXT,
                user_agent TEXT,
                source TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        # Crear índices para búsquedas rápidas
        cur.execute('CREATE INDEX IF NOT EXISTS idx_visitors_external_id ON visitors(external_id);')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_visitors_fbclid ON visitors(fbclid);')
        conn.commit()
        cur.close()
        conn.close()
        print("✅ PostgreSQL (Supabase) conectada e inicializada.")
    except Exception as e:
        print(f"❌ Error init_db: {e}")

def save_visitor(external_id: str, fbclid: str, ip_address: str, user_agent: str, source: str = "pageview"):
    """Guarda un registro de visitante en PostgreSQL"""
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cur = conn.cursor()
        # PostgreSQL usa %s para placeholders
        cur.execute(
            "INSERT INTO visitors (external_id, fbclid, ip_address, user_agent, source) VALUES (%s, %s, %s, %s, %s)",
            (external_id, fbclid, ip_address, user_agent[:500] if user_agent else None, source)
        )
        conn.commit()
        cur.close()
        conn.close()
        print(f"[DB] Visitor saved: fbclid={bool(fbclid)}, source={source}")
    except Exception as e:
        print(f"❌ Error save_visitor: {e}")

def get_visitor_by_external_id(external_id: str):
    """Recupera el fbclid de un visitante por su external_id"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT fbclid FROM visitors WHERE external_id = %s AND fbclid IS NOT NULL ORDER BY timestamp DESC LIMIT 1",
            (external_id,)
        )
        row = cur.fetchone()
        cur.close()
        conn.close()
        return row[0] if row else None
    except Exception as e:
        print(f"❌ Error get_visitor: {e}")
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
# ENDPOINTS - HEALTH CHECK (Para UptimeRobot)
# =================================================================
@app.get("/health")
async def health_check():
    """Health check + verificación de DB"""
    db_status = "connected" if get_db_connection() else "not configured"
    return JSONResponse({
        "status": "healthy",
        "database": db_status,
        "timestamp": datetime.now().isoformat(),
        "service": "Jorge Aguirre Flores Web"
    })

@app.get("/ping")
async def ping():
    return "pong"

# =================================================================
# RUTAS DE LA PÁGINA
# =================================================================
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, response: Response, background_tasks: BackgroundTasks):
    """PÁGINA DE INICIO - Con tracking y persistencia en Supabase"""
    event_id = str(int(time.time() * 1000))
    
    client_ip = request.client.host
    user_agent = request.headers.get('user-agent', '')
    current_url = str(request.url)
    
    # Capturar fbclid de la URL
    fbclid = request.query_params.get('fbclid')
    
    # Generar external_id único
    external_id = generate_external_id(client_ip, user_agent)
    
    # Si no hay fbclid en URL, buscar en la base de datos
    if not fbclid:
        fbclid = get_visitor_by_external_id(external_id)
        if fbclid:
            print(f"[DB] Recovered fbclid from PostgreSQL")
    
    # Guardar en base de datos si hay fbclid valioso
    if fbclid:
        fbc_value = generate_fbc(fbclid)
        response.set_cookie(key="_fbc", value=fbc_value, max_age=90*24*60*60, httponly=True, samesite="lax")
        # Guardar en DB (background task)
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
    """TRACKING DE LEAD - Con recuperación de fbclid de PostgreSQL"""
    data = await request.json()
    
    client_ip = request.client.host
    user_agent = request.headers.get('user-agent', '')
    external_id = generate_external_id(client_ip, user_agent)
    
    # Recuperar fbclid de cookie o base de datos
    fbclid = None
    fbc_cookie = request.cookies.get("_fbc")
    if fbc_cookie and fbc_cookie.startswith("fb.1."):
        parts = fbc_cookie.split(".")
        if len(parts) >= 4:
            fbclid = parts[3]
    
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
