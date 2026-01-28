import httpx
import asyncio
import json

# Configuration
API_URL = "https://evolution-whatsapp-zn13.onrender.com"
API_KEY = "JorgeSecureKey123"
INSTANCE = "NataliaCoreV1"
WEBHOOK_URL = "https://natalia-brain.onrender.com/webhook/evolution"

async def fix_ears():
    print(f"👂 FIXING DIGITAL EARS (WEBHOOKS) FOR: {INSTANCE}")
    print(f"Target Brain: {WEBHOOK_URL}")
    
    headers = {
        "apikey": API_KEY,
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient(timeout=20.0) as client:
        # 0. Check Health/Status
        print("\n🏥 Checking Instance Status...")
        try:
            resp = await client.get(f"{API_URL}/instance/connectionState/{INSTANCE}", headers=headers)
            print(f"Status: {resp.status_code}")
            if resp.status_code != 200:
                print(f"⚠️ Instance might be missing or down. Response: {resp.text}")
            else:
                print(f"✅ Instance Found: {resp.text}")
        except Exception as e:
            print(f"❌ Connection Check Failed: {e}")
            return

        # 1. Try Endpoint Variant A: /webhook/instance/{instance}
        print("\n🔄 Attempting Endpoint Variant A: /webhook/instance/{instance} ...")
        payload = {
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
        
        try:
            # Note: endpoint structure for Evolution v1.6+ / v2.0
            resp = await client.post(f"{API_URL}/webhook/instance/{INSTANCE}", json=payload, headers=headers)
            print(f"Status: {resp.status_code}")
            
            if resp.status_code == 200 or resp.status_code == 201:
                print("✅ SUCCESS! Webhook Set via Variant A.")
                return
            else:
                print(f"⚠️ Variant A Failed: {resp.text}")
        except Exception as e:
            print(f"❌ Variant A Error: {e}")

        # 2. Try Endpoint Variant B: /webhook/set/{instance} (Retry)
        print("\n🔄 Attempting Endpoint Variant B: /webhook/set/{instance} ...")
        try:
            resp = await client.post(f"{API_URL}/webhook/set/{INSTANCE}", json=payload, headers=headers)
            print(f"Status: {resp.status_code}")
            if resp.status_code == 200:
                print("✅ SUCCESS! Webhook Set via Variant B.")
            else:
                 print(f"⚠️ Variant B Failed: {resp.text}")

        except Exception as e:
            print(f"❌ Variant B Error: {e}")

if __name__ == "__main__":
    asyncio.run(fix_ears())
