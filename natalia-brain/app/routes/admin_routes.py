from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
import httpx
import logging
from app.config import settings

router = APIRouter()
logger = logging.getLogger("AdminRouter")

# HTML Template for QR Code
QR_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Natalia Brain | WhatsApp Connect</title>
    <meta http-equiv="refresh" content="10"> <!-- Auto-refresh every 10s -->
    <style>
        body { font-family: 'Inter', sans-serif; background: #0f172a; color: white; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; }
        .card { background: #1e293b; padding: 2rem; border-radius: 1rem; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); text-align: center; max-width: 400px; width: 90%; }
        h1 { font-size: 1.5rem; margin-bottom: 1rem; color: #38bdf8; }
        .status { margin-bottom: 1.5rem; padding: 0.5rem; border-radius: 0.5rem; font-weight: bold; }
        .status.open { background: #22c55e; color: #fff; }
        .status.connecting { background: #eab308; color: #000; }
        img { border: 4px solid #fff; border-radius: 0.5rem; max-width: 100%; }
        p { color: #94a3b8; margin-top: 1rem; }
        .btn { display: inline-block; padding: 0.75rem 1.5rem; background: #3b82f6; color: white; text-decoration: none; border-radius: 0.5rem; margin-top: 1rem; transition: background 0.2s; }
        .btn:hover { background: #2563eb; }
    </style>
</head>
<body>
    <div class="card">
        <h1>🔗 WhatsApp Connector (Prod)</h1>
        
        <div class="status {{ state_class }}">
            Status: {{ state_text }}
        </div>

        {% if qr_base64 %}
            <img src="{{ qr_base64 }}" alt="QR Code">
            <p>Scan this QR with WhatsApp (Linked Devices)</p>
        {% elif state == 'open' %}
             <div style="font-size: 4rem;">✅</div>
             <p>Natalia is fully connected to WhatsApp!</p>
        {% else %}
             <p>Waiting for instance initialization...</p>
        {% endif %}
        
        <a href="/admin/whatsapp" class="btn">Refresh Status</a>
    </div>
</body>
</html>
"""

@router.get("/admin/whatsapp", response_class=HTMLResponse)
async def admin_whatsapp_qr():
    """
    Renders the WhatsApp status or QR code for 'NataliaCoreProd'.
    Auto-creates the instance if it doesn't exist.
    """
    instance = settings.EVOLUTION_INSTANCE # e.g. "NataliaCoreProd"
    api_url = settings.EVOLUTION_API_URL
    headers = {
        "apikey": settings.EVOLUTION_API_KEY,
        "Content-Type": "application/json"
    }

    state = "unknown"
    qr_base64 = None

    async with httpx.AsyncClient() as client:
        try:
            # 1. Check Connection State
            status_res = await client.get(
                f"{api_url}/instance/connectionState/{instance}", 
                headers=headers
            )
            
            if status_res.status_code == 404:
                # Instance doesn't exist -> Create it
                create_res = await client.post(
                    f"{api_url}/instance/create",
                    json={
                        "instanceName": instance, 
                        "token": instance, 
                        "qrcode": True,
                        "integration": "WHATSAPP-BAILEYS"
                    },
                    headers=headers
                )
                logger.info(f"Created Instance {instance}: {create_res.status_code}")
                state = "connecting"
            else:
                data = status_res.json()
                # Evolution v2 structure usually: { "instance": { "state": "open", ... } }
                if "instance" in data:
                     state = data["instance"].get("state", "unknown")
                else:
                     # Fallback for some versions
                     state = data.get("state", "unknown")

            # 2. If connecting/close, fetch QR
            if state in ["connecting", "close", "undefined"]:
                qr_res = await client.get(
                    f"{api_url}/instance/connect/{instance}", 
                    headers=headers
                )
                if qr_res.status_code == 200:
                    qr_data = qr_res.json()
                    if "base64" in qr_data:
                        qr_base64 = qr_data["base64"] # usually includes 'data:image/png;base64,...' prefix

        except Exception as e:
            logger.error(f"Error connecting to Evolution: {e}")
            return f"<h1>Error connecting to Evolution API</h1><p>{e}</p>"

    # 3. Render Template (Simple String Replace for speed/robustness without Jinja dependency issues here)
    html = QR_TEMPLATE
    
    # State Class
    state_class = "open" if state == "open" else "connecting"
    
    html = html.replace("{{ state_text }}", state.upper())
    html = html.replace("{{ state_class }}", state_class)
    
    # Logic blocks simulation
    if qr_base64:
        # Show QR block
        img_tag = f'<img src="{qr_base64}" alt="QR Code">'
        html = html.replace("{% if qr_base64 %}", "") 
        html = html.replace('{{ qr_base64 }}', qr_base64)
        # Remove the 'elif state == open' block
        # This is a bit hacky string replace, but safe for this specific constant template
        # Let's clean up the template block markers manually for robustness
        html = html.split("{% elif")[0] + f'{img_tag}<p>Scan this QR with WhatsApp (Linked Devices)</p></div></body></html>'
        
    elif state == "open":
        # Show Success block
        success_block = '<div style="font-size: 4rem;">✅</div><p>Natalia is fully connected to WhatsApp!</p>'
        # Hacky parse again: Find the elif block
        # To avoid complexity, let's just rewrite the return logic clearly:
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Natalia Brain | Connected</title>
    <meta http-equiv="refresh" content="30">
    <style>
        body {{ font-family: 'Inter', sans-serif; background: #0f172a; color: white; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; }}
        .card {{ background: #1e293b; padding: 2rem; border-radius: 1rem; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); text-align: center; max-width: 400px; width: 90%; }}
        .btn {{ display: inline-block; padding: 0.75rem 1.5rem; background: #3b82f6; color: white; text-decoration: none; border-radius: 0.5rem; margin-top: 1rem; }}
    </style>
</head>
<body>
    <div class="card">
        <h1>🔗 WhatsApp Connector (Prod)</h1>
        <div style="font-size: 4rem;">✅</div>
        <p style="color: #4ade80; font-weight: bold; font-size: 1.2rem;">ONLINE</p>
        <p style="color: #94a3b8;">Instance: {instance}</p>
        <a href="/admin/whatsapp" class="btn">Refresh</a>
    </div>
</body>
</html>
"""
    else:
        # Fallback/Loading
        html = html.replace("{% if qr_base64 %}", "<!-- no qr -->")
        html = html.replace("{% elif state == 'open' %}", "<!-- not open -->")
        html = html.split("{% else %}")[1].split("{% endif %}")[0] # Extract waiting block
        
        # Actually, let's just return a simpler clean HTML for this case too to avoid parsing headaches
        return f"""
<!DOCTYPE html>
<html>
<head><title>Natalia Status</title><meta http-equiv="refresh" content="5"></head>
<body style="background:#0f172a; color:white; display:flex; justify-content:center; align-items:center; height:100vh; font-family:sans-serif;">
    <div style="text-align:center">
        <h1>Status: {state}</h1>
        <p>Waiting for QR code generation...</p>
        <a href="/admin/whatsapp" style="color:#38bdf8">Refresh Manually</a>
    </div>
</body>
</html>
"""

    return HTMLResponse(content=html)
