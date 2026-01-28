import httpx
import asyncio
import os
import sys

# Configuration
API_URL = "https://evolution-whatsapp-zn13.onrender.com"
API_KEY = "JorgeSecureKey123"
INSTANCE = "NataliaCoreV1"
# Target Brain URL (Production)
WEBHOOK_URL = "https://natalia-brain.onrender.com/webhook/evolution"

async def setup_ears():
    print(f"👂 CONFIGURE WEBHOOKS (DIGITAL EARS) FOR: {INSTANCE}")
    print(f"Target: {WEBHOOK_URL}")
    
    headers = {
        "apikey": API_KEY,
        "Content-Type": "application/json"
    }
    
    # Evolution V2 Webhook Configuration
    payload = {
        "enabled": True,
        "url": WEBHOOK_URL,
        "webhookByEvents": True,
        "events": [
            "MESSAGES_UPSERT",       # Incoming messages
            "MESSAGES_UPDATE",       # Status updates (read/delivered)
            "SEND_MESSAGE",          # Outgoing messages (for sync)
            "CONNECTION_UPDATE"      # Disconnect alerts
        ]
    }
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            url = f"{API_URL}/webhook/set/{INSTANCE}"
            print(f"POST {url}")
            resp = await client.post(url, json=payload, headers=headers)
            
            print(f"Status: {resp.status_code}")
            print(f"Response: {resp.text}")
            
            if resp.status_code == 200 or resp.status_code == 201:
                print("✅ EARS ACTIVE: Webhook configured successfully.")
            else:
                print("❌ Webhook configuration failed.")
                
        except Exception as e:
            print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    asyncio.run(setup_ears())
