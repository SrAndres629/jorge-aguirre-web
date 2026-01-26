import httpx
import asyncio
import json
from datetime import datetime

TARGET_URL = "http://localhost:8081/webhook"

MOCK_PAYLOADS = {
    "MESSAGES_UPSERT": {
        "event": "MESSAGES_UPSERT",
        "instance": "JorgeMain",
        "data": {
            "key": {"remoteJid": "59164714751@s.whatsapp.net", "fromMe": False, "id": "ABC123XYZ"},
            "message": {"conversation": "Hola Jorge, quiero agendar un Microblading para el lunes."},
            "pushName": "Cliente VIP"
        }
    },
    "CONNECTION_UPDATE": {
        "event": "CONNECTION_UPDATE",
        "instance": "JorgeMain",
        "data": {
            "state": "open",
            "statusReason": 200
        }
    },
    "CALL": {
        "event": "CALL",
        "instance": "JorgeMain",
        "data": {
            "from": "59164714751@s.whatsapp.net",
            "id": "call_999",
            "status": "offer"
        }
    }
}

async def simulate_event(event_name):
    payload = MOCK_PAYLOADS.get(event_name)
    if not payload:
        print(f"❌ Event {event_name} not found in mocks.")
        return

    print(f"📡 Simulating {event_name}...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(TARGET_URL, json=payload, timeout=5.0)
            print(f"✅ Response ({response.status_code}): {response.json()}")
    except Exception as e:
        print(f"❌ Connection error: {e}. Is the listener running?")

async def main():
    print("🧪 Evolution API Event Simulator")
    print("1. Simulate Message (MESSAGES_UPSERT)")
    print("2. Simulate Connection (CONNECTION_UPDATE)")
    print("3. Simulate Call (CALL)")
    print("4. Run All")
    
    choice = input("Select an option (1-4): ")
    
    if choice == "1": await simulate_event("MESSAGES_UPSERT")
    elif choice == "2": await simulate_event("CONNECTION_UPDATE")
    elif choice == "3": await simulate_event("CALL")
    elif choice == "4":
        for evt in MOCK_PAYLOADS.keys():
            await simulate_event(evt)
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    asyncio.run(main())
