import httpx
import asyncio
import json

# Configuration
API_URL = "https://evolution-whatsapp-zn13.onrender.com"
API_KEY = "JorgeSecureKey123"
INSTANCE = "NataliaCoreV1"
WEBHOOK_URL = "https://natalia-brain.onrender.com/webhook/evolution"

async def fix_ears_v2():
    print(f"👂 FIXING DIGITAL EARS (ATTEMPT 2) FOR: {INSTANCE}")
    
    headers = {
        "apikey": API_KEY,
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient(timeout=20.0) as client:
        # Variant C: Wrapped Payload
        print("\n🔄 Attempting Payload Variant C (Wrapped)...")
        
        # Proper Evolution v2 might expect this nesting
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
        
        try:
            resp = await client.post(f"{API_URL}/webhook/instance/{INSTANCE}", json=payload, headers=headers)
            print(f"Status: {resp.status_code}")
            print(f"Response: {resp.text}")
            
            if resp.status_code == 200 or resp.status_code == 201:
                print("✅ SUCCESS! Webhook Set via Variant C.")
                return
        except Exception as e:
            print(f"❌ Variant C Error: {e}")

        # Variant D: Try '/webhook/find' to see current config (Debugging)
        print("\n🔍 Debugging: Checking Current Webhook Config...")
        try:
             resp = await client.get(f"{API_URL}/webhook/find/{INSTANCE}", headers=headers)
             print(f"Status: {resp.status_code}")
             print(f"Current Config: {resp.text}")
        except Exception as e:
             print(f"❌ Debug Check Error: {e}")

if __name__ == "__main__":
    asyncio.run(fix_ears_v2())
