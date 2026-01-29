import httpx
import asyncio
import json

API_URL = "https://evolution-whatsapp-zn13.onrender.com"
API_KEY = "JorgeSecureKey123"
INSTANCE = "NataliaBrain"

async def debug_create():
    headers = {"apikey": API_KEY, "Content-Type": "application/json"}
    print(f"🐛 DEBUG CREATION FOR: {INSTANCE}")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Minimal Body
        body = {
            "instanceName": INSTANCE,
            "token": API_KEY,
            "qrcode": True
        }
        resp = await client.post(f"{API_URL}/instance/create", json=body, headers=headers)
        print(f"Result: {resp.status_code}")
        print(f"Full Response: {resp.text}")

if __name__ == "__main__":
    asyncio.run(debug_create())
