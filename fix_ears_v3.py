import httpx
import asyncio
import json

API_URL = "https://evolution-whatsapp-zn13.onrender.com"
API_KEY = "JorgeSecureKey123"
INSTANCE = "NataliaCoreV1"
WEBHOOK_URL = "https://natalia-brain.onrender.com/webhook/evolution"

async def fix_ears_v3():
    print(f"👂 FIXING DIGITAL EARS (ATTEMPT 3) FOR: {INSTANCE}")
    headers = {"apikey": API_KEY, "Content-Type": "application/json"}

    # Payload Wrapped in 'webhook' key
    payload = {
        "webhook": {
            "enabled": True,
            "url": WEBHOOK_URL,
            "webhookByEvents": True,
            "events": [
                "MESSAGES_UPSERT",
                "MESSAGES_UPDATE",
                "SEND_MESSAGE",
                "CONNECTION_UPDATE"
            ]
        }
    }
    
    async with httpx.AsyncClient(timeout=20.0) as client:
        # Endpoint: /webhook/set/{instance}
        url = f"{API_URL}/webhook/set/{INSTANCE}"
        print(f"\n🚀 POST {url}")
        
        try:
            resp = await client.post(url, json=payload, headers=headers)
            print(f"Status: {resp.status_code}")
            print(f"Response: {resp.text}")
            
            if resp.status_code == 200 or resp.status_code == 201:
                print("✅ EARS FIXED. Webhook configured.")
            else:
                 print("⚠️ Configuration Failed.")
                 
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(fix_ears_v3())
