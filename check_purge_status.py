import httpx
import asyncio
import sys

# Configuration
API_URL = "https://evolution-whatsapp-zn13.onrender.com"
API_KEY = "JorgeSecureKey123"
INSTANCE = "NataliaBrain"
WEBHOOK_URL = "https://natalia-brain.onrender.com/webhook/evolution"

async def check_and_finalize():
    print(f"🕵️ CHECKING STATUS FOR: {INSTANCE}")
    headers = {"apikey": API_KEY, "Content-Type": "application/json"}
    
    async with httpx.AsyncClient(timeout=20.0) as client:
        # 1. CHECK STATUS
        try:
            resp = await client.get(f"{API_URL}/instance/connectionState/{INSTANCE}", headers=headers)
            print(f"   Status Response: {resp.status_code} | {resp.text}")
            
            if resp.status_code == 200:
                data = resp.json()
                state = data.get("instance", {}).get("state") # Evolution v1.6 structure?
                # Or Evolution v2: data.get("state")
                
                print(f"   Current State: {state}")
                
                if state == "open":
                    print("\n✅ CONNECTION CONFIRMED: OPEN")
                    # 2. APPLY WEBHOOK (Only if open)
                    print("   🔌 Applying Critical Webhook...")
                    webhook_body = {
                        "webhook": {
                            "enabled": True,
                            "url": WEBHOOK_URL,
                            "webhookByEvents": True,
                            "events": ["MESSAGES_UPSERT"]
                        }
                    }
                    w_resp = await client.post(f"{API_URL}/webhook/set/{INSTANCE}", json=webhook_body, headers=headers)
                    print(f"   Webhook Result: {w_resp.status_code} | {w_resp.text}")
                else:
                    print("\n⏳ WAITING FOR SCAN. State is NOT 'open' yet.")
            else:
                print("   ❌ Instance not found or error.")
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_and_finalize())
