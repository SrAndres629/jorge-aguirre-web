import httpx
import asyncio
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from app.config import settings

async def create_raw():
    url = f"{settings.EVOLUTION_API_URL}/instance/create"
    headers = {"apikey": settings.EVOLUTION_API_KEY}
    payload = {
        "instanceName": settings.EVOLUTION_INSTANCE, 
        "token": settings.EVOLUTION_API_KEY,
        "qrcode": True,
        "integration": "WHATSAPP-BAILEYS" 
    }
    print(f"Creating instance at {url} with:")
    print(f"Payload: {payload}")
    print("-" * 50)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.post(url, json=payload, headers=headers)
            print(f"Status: {resp.status_code}")
            print(f"Response: {resp.text}")
        except Exception as e:
            print(f"❌ Error: {repr(e)}")

if __name__ == "__main__":
    asyncio.run(create_raw())
