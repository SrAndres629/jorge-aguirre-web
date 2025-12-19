from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.gzip import GZipMiddleware
import requests
import time
import uvicorn

# =================================================================
# CONFIGURACIÓN DEL SISTEMA
# =================================================================
app = FastAPI()

# GZipMiddleware: Comprime la web antes de enviarla. 
# Esto hace que la carga sea hasta 5x más rápida en móviles con poco internet.
app.add_middleware(GZipMiddleware, minimum_size=1000)

# IDs de Marketing (Meta Ads)
META_PIXEL_ID = "1412977383680793"
META_ACCESS_TOKEN = "EAAmeW8lDnZAQBQJ61ZC4CCfcNFZBZAQuFBJE06SOZB1AvAexCyUVY3ajvW9u46dvMoYvFMSudqhdYNW4A2PQicr0tcUZBG0itr9ZBUZAuzq7eC83avJT9ox75W5WrncNheJ928IZAo4BxB403x8eeckpdYU8dgu84pHxZC0lEVssgLWWE1Xm30JZCuQbKKkoZB2dkgZDZD"

# Configuración de carpetas: le decimos a Python dónde están los archivos
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# =================================================================
# LÓGICA DE TRACKING (CONVERSIONS API - CAPI)
# =================================================================
def send_to_meta_capi(event_name: str, event_source_url: str, client_ip: str, user_agent: str, event_id: str):
    """
    ENVÍO AL SERVIDOR DE META: Esta es "la ciencia oculta" de tu web.
    En lugar de que el navegador mande los datos (que a veces el AdBlock bloquea),
    Python los manda directamente a los servidores de Facebook.
    Esto hace que tus campañas de anuncios sean mucho más precisas.
    """
    url = f"https://graph.facebook.com/v19.0/{META_PIXEL_ID}/events"
    
    payload = {
        "data": [
            {
                "event_name": event_name,
                "event_time": int(time.time()),
                "event_id": event_id, # ID único para que FB no cuente dos veces lo mismo
                "action_source": "website",
                "event_source_url": event_source_url,
                "user_data": {
                    "client_ip_address": client_ip,
                    "client_user_agent": user_agent,
                }
            }
        ],
        "access_token": META_ACCESS_TOKEN
    }
    
    try:
        response = requests.post(url, json=payload)
        # Log en consola para que veas si Meta recibió el dato correctamente
        print(f"[META CAPI] Evento {event_name} enviado. Status: {response.status_code}")
    except Exception as e:
        print(f"[ERROR CAPI]: {e}")

# =================================================================
# RUTAS DE LA PÁGINA
# =================================================================

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, background_tasks: BackgroundTasks):
    """
    PÁGINA DE INICIO: Cuando alguien entra a jorgeaguirreflores.com
    """
    # Creamos un ID único para esta visita (Deduplicación)
    event_id = str(int(time.time() * 1000))
    
    # Capturamos datos del visitante
    client_ip = request.client.host
    user_agent = request.headers.get('user-agent')
    current_url = str(request.url)

    # El tracking se corre "en el fondo" (background_tasks) 
    # para que la página cargue de inmediato sin esperar a los servidores de Meta.
    background_tasks.add_task(
        send_to_meta_capi, "PageView", current_url, client_ip, user_agent, event_id
    )
    
    # Enviamos la web al navegador del cliente
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "pixel_id": META_PIXEL_ID,
        "pageview_event_id": event_id
    })

@app.post("/track-lead")
async def track_lead(request: Request, background_tasks: BackgroundTasks):
    """
    TRACKING DE BOTÓN WHATSAPP: Se dispara cuando alguien hace clic en "Valoración".
    """
    data = await request.json()
    
    background_tasks.add_task(
        send_to_meta_capi, 
        "Lead", 
        str(request.url), 
        request.client.host, 
        request.headers.get('user-agent'),
        data.get("event_id")
    )
    return {"status": "success"}

@app.post("/track-viewcontent")
async def track_viewcontent(request: Request, background_tasks: BackgroundTasks):
    """
    TRACKING DE VIEWCONTENT: Se dispara cuando el usuario ve una sección de servicio.
    Esto permite crear públicos de retargeting segmentados por interés (cejas, labios, ojos).
    """
    data = await request.json()
    event_id = f"vc_{int(time.time() * 1000)}"
    
    # Enviar ViewContent a Meta CAPI
    url = f"https://graph.facebook.com/v19.0/{META_PIXEL_ID}/events"
    
    payload = {
        "data": [
            {
                "event_name": "ViewContent",
                "event_time": int(time.time()),
                "event_id": event_id,
                "action_source": "website",
                "event_source_url": str(request.url),
                "custom_data": {
                    "content_name": data.get("service"),
                    "content_category": data.get("category"),
                    "content_type": "service"
                },
                "user_data": {
                    "client_ip_address": request.client.host,
                    "client_user_agent": request.headers.get('user-agent'),
                }
            }
        ],
        "access_token": META_ACCESS_TOKEN
    }
    
    def send_viewcontent():
        try:
            response = requests.post(url, json=payload)
            print(f"[META CAPI] ViewContent {data.get('category')} enviado. Status: {response.status_code}")
        except Exception as e:
            print(f"[ERROR CAPI ViewContent]: {e}")
    
    background_tasks.add_task(send_viewcontent)
    return {"status": "success", "category": data.get("category")}

# ARRANQUE DEL SISTEMA
if __name__ == "__main__":
    # 0.0.0.0 significa que es accesible desde cualquier red (internet) en el puerto 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
