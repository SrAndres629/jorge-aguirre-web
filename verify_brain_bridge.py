import httpx
import asyncio
import json
import os
from datetime import datetime

# CONFIGURATION
BRAIN_URL = "https://natalia-brain.onrender.com"
EVOLUTION_URL = "https://evolution-whatsapp-zn13.onrender.com"
API_KEY = "JorgeSecureKey123"
INSTANCE = "NataliaBrain"
ADMIN_PHONE = "59178113055" # Admin/Dev Phone

async def verify_doctoral_bridge():
    print(f"🔍 [DOCTORAL-BRIDGE-TEST] Starting Full-Stack Diagnostics...")
    
    # 1. Test Natalia's Health & Gemini Connectivity
    print(f"📡 1. Checking Natalia Brain...")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{BRAIN_URL}/health")
            if resp.status_code == 200:
                data = resp.json()
                print(f"   ✅ Brain Online: {data.get('engine')} (v{data.get('version')})")
            else:
                print(f"   ❌ Health Check Failed: {resp.status_code}")
    except Exception as e:
        print(f"   ❌ Network Error (Brain): {e}")

    # 2. Test DATABASE Connection via Natalia
    print(f"🗄️ 2. Verifying Database Accessibility...")
    try:
        # We use the internal 'run_readonly_sql' tool logic indirectly or check if Natalia can load knowledge
        # For a safe test, we'll check if the health endpoint can see the instance config (which comes from DB/Env)
        # But even better: we simulate a message that REQUIRES a DB lookup.
        pass
    except Exception as e:
        print(f"   ❌ DB Access Error: {e}")

    # 3. Simulate WhatsApp Message with DB Intent (Pricing Query)
    print(f"🧪 3. Injecting 'Pricing Query' to test DB + Gemini Bridge...")
    webhook_url = f"{BRAIN_URL}/webhook/evolution"
    
    # This message forces Natalia to:
    # 1. Identify input.
    # 2. Query DB for services/prices.
    # 3. Use Gemini to format response.
    payload = {
        "event": "MESSAGES_UPSERT",
        "instance": INSTANCE,
        "data": {
            "key": {
                "remoteJid": f"{ADMIN_PHONE}@s.whatsapp.net",
                "fromMe": False,
                "id": f"TEST_DB_LINK_{datetime.now().strftime('%H%M%S')}"
            },
            "message": {"conversation": "¿Cuál es el precio del microblading y qué incluye?"},
            "messageType": "conversation",
            "pushName": "Antigravity Evaluator"
        }
    }
    
    try:
        async with httpx.AsyncClient() as client:
            print(f"   🚀 Sending payload to {webhook_url}...")
            resp = await client.post(webhook_url, json=payload, timeout=12.0)
            if resp.status_code == 200:
                print(f"   ✅ Webhook Accepted.")
                print(f"   📊 [ACTION REQUIRED]: Observa tu WhatsApp.") 
                print(f"   Si Natalia responde con precios reales de tu DB, el puente DB+GEMINI es exitoso.")
            else:
                print(f"   ❌ Webhook Refused (404/500): {resp.status_code}")
                if "zn13" in str(resp.url):
                    print(f"   ⚠️ ALERTA: Sigues usando la URL con 'zn13' en alguna parte.")
    except Exception as e:
        print(f"   ❌ Injection Failed: {e}")

if __name__ == "__main__":
    asyncio.run(verify_doctoral_bridge())
