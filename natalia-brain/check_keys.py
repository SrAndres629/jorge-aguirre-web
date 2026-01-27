import httpx
import asyncio
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from app.config import settings

CANDIDATE_KEYS = [
    settings.EVOLUTION_API_KEY,           # JorgeSecureKey123
    "429683C4C977415CAAFCCE10F7D57E11",   # Default from env.config.ts
    "123456",                             # Common weak default
    "B6D711FCDE4D4FD5936544120E713976"    # Another common default
]

async def check_keys():
    base_url = settings.EVOLUTION_API_URL
    print(f"🔐 Testing API Keys against {base_url}...")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        for i, key in enumerate(CANDIDATE_KEYS):
            masked = key[:4] + "***" if key else "None"
            print(f"\nArguments [{i}]: Testing Key={masked}")
            
            try:
                # We use fetch instances as a lightweight auth check
                resp = await client.get(f"{base_url}/instance/fetchInstances", headers={"apikey": key})
                
                print(f"Status: {resp.status_code}")
                if resp.status_code == 200:
                    print(f"🎉 SUCCESS! The correct key is: {key}")
                    return
                elif resp.status_code == 403:
                    print("❌ Forbidden (Wrong Key)")
                else:
                    print(f"⚠️ Unexpected status: {resp.status_code}")
            except Exception as e:
                print(f"❌ Connection Failed: {e}")

    print("\n💀 All keys failed. Please check Render Environment Variables.")

if __name__ == "__main__":
    asyncio.run(check_keys())
