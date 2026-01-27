import httpx
import asyncio
import sys
import os

# Add the current directory to sys.path
sys.path.append(os.getcwd())

from app.config import settings

async def test_raw():
    url = f"{settings.EVOLUTION_API_URL}/instance/connectionState/{settings.EVOLUTION_INSTANCE}"
    # Mask API Key for security in logs
    masked_key = settings.EVOLUTION_API_KEY[:4] + "***" if settings.EVOLUTION_API_KEY else "None"
    
    print(f"Target URL: {url}")
    print(f"API Key: {masked_key}")
    print("-" * 50)
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(url, headers={"apikey": settings.EVOLUTION_API_KEY})
            print(f"Response Status: {resp.status_code}")
            print(f"Response Body: {resp.text}")
        except Exception as e:
            print(f"❌ Connection Error: {repr(e)}")

if __name__ == "__main__":
    asyncio.run(test_raw())
