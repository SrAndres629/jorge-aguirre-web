
import httpx
import asyncio
import json
import os
import sys

# Add project root to path to import config if needed, 
# but for now we'll use env vars directly or defaults.

API_KEY = os.getenv("EVOLUTION_API_KEY", "B89599B2-37E4-4DCA-92D3-87F8674C7D69")
BASE_URL = os.getenv("EVOLUTION_API_URL", "http://localhost:8081")
INSTANCE_NAME = "JorgeMain"
# Use the internal docker name if running inside docker, else localhost with mapped port
# But this script is likely run from host.
# If run from host, use localhost:8001 (which we mapped to evolution_mcp_server:8001)
WEBHOOK_URL = "http://evolution_mcp_server:8001/webhook"

async def setup():
    print(f"🔧 Configuring Evolution API Instance: {INSTANCE_NAME}")
    print(f"📡 API URL: {BASE_URL}")
    print(f"🔗 Webhook Target: {WEBHOOK_URL}")

    async with httpx.AsyncClient(headers={"apikey": API_KEY}, timeout=30.0) as client:
        
        # 1. Check if instance exists and delete it
        print(f"\n1️⃣  Checking existing instance...")
        try:
            res = await client.get(f"{BASE_URL}/instance/fetchInstances")
            if res.status_code == 200:
                instances = res.json()
                exists = any(i['instance']['instanceName'] == INSTANCE_NAME for i in instances)
                if exists:
                    print(f"   Instance found. Deleting...")
                    await client.delete(f"{BASE_URL}/instance/delete/{INSTANCE_NAME}")
                    await asyncio.sleep(2) # Wait for cleanup
                else:
                    print("   Instance not found.")
        except Exception as e:
            print(f"   Error checking instances: {e}")

        # 2. Create Instance
        print(f"\n2️⃣  Creating instance {INSTANCE_NAME}...")
        payload = {
            "instanceName": INSTANCE_NAME,
            "token": "1505BD4F6F5C-42EB-B731-D6CA1643A73D",
            "qrcode": True,
            "integration": "WHATSAPP-BAILEYS"
        }
        try:
            res = await client.post(f"{BASE_URL}/instance/create", json=payload)
            print(f"   Result: {res.status_code} - {res.text}")
        except Exception as e:
            print(f"   Failed to create instance: {e}")
            return

        # 3. Configure Settings
        print("\n3️⃣  Configuring settings (Persistence & Behavior)...")
        settings_payload = {
            "rejectCall": True,
            "msgCall": "No acepto llamadas. Por favor envía un mensaje de texto.",
            "groupsIgnore": True,
            "alwaysOnline": True,
            "readMessages": True,
            "readStatus": True,
            "syncFullHistory": True
        }
        try:
            res = await client.post(f"{BASE_URL}/settings/set/{INSTANCE_NAME}", json=settings_payload)
            print(f"   Settings Result: {res.status_code}")
        except Exception as e:
             print(f"   Failed to set settings: {e}")

        # 4. Configure Webhook
        print("\n4️⃣  Configuring Webhook...")
        webhook_payload = {
            "url": WEBHOOK_URL,
            "enabled": True,
            "events": [
                "MESSAGES_UPSERT",
                "MESSAGES_UPDATE",
                "SEND_MESSAGE",
                "CONNECTION_UPDATE",
                "PRESENCE_UPDATE",
                "CHATS_SET",
                "CHATS_UPSERT"
            ]
        }
        try:
            res = await client.post(f"{BASE_URL}/webhook/set/{INSTANCE_NAME}", json=webhook_payload)
            print(f"   Webhook Result: {res.status_code} - {res.text}")
        except Exception as e:
            print(f"   Failed to set webhook: {e}")

    print("\n✅ Setup Complete!")
    print("👉 Go to Evolution Manager or check logs to scan the QR Code.")

if __name__ == "__main__":
    asyncio.run(setup())
