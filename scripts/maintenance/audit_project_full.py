
import asyncio
import httpx
import sys
import os

# Configuration
EVOLUTION_URL = "http://localhost:8081"
EVOLUTION_KEY = os.getenv("EVOLUTION_API_KEY", "B89599B2-37E4-4DCA-92D3-87F8674C7D69")
WEB_URL = "http://localhost:8000"
N8N_URL = "http://localhost:5678"
MCP_URL = "http://localhost:8002"

async def check_service(name, url, expected_status=200):
    print(f"🔸 Checking {name} ({url})...", end=" ")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.get(url)
            if res.status_code == expected_status or (res.status_code < 500):
                print(f"✅ UP ({res.status_code})")
                return True
            else:
                print(f"❌ ERROR ({res.status_code})")
                return False
    except Exception as e:
        print(f"❌ FAIL ({e})")
        return False

async def check_evolution_db():
    print(f"🔸 Checking Evolution -> Supabase Connection...", end=" ")
    url = f"{EVOLUTION_URL}/instance/fetchInstances"
    try:
        async with httpx.AsyncClient(headers={"apikey": EVOLUTION_KEY}, timeout=10.0) as client:
            res = await client.get(url)
            if res.status_code == 200:
                instances = res.json()
                count = len(instances)
                print(f"✅ CONNECTED (Found {count} instances)")
                return True
            else:
                print(f"❌ API Error ({res.status_code})")
                return False
    except Exception as e:
        print(f"❌ Connection Failed ({e})")
        return False

async def main():
    print("🚀 STARTING PROJECT FULL AUDIT\n")
    
    tasks = [
        check_service("Web App", f"{WEB_URL}/health"),
        check_service("Evolution API", EVOLUTION_URL, 404), # 404 is ok for root
        check_service("n8n Automation", N8N_URL),
        # check_service("Evolution MCP", MCP_URL) # MCP might not have GET /
    ]
    
    results = await asyncio.gather(*tasks)
    
    db_ok = await check_evolution_db()
    
    print("\n📝 SUMMARY:")
    all_ok = all(results) and db_ok
    if all_ok:
        print("✅ ALL SYSTEMS OPERATIONAL")
        sys.exit(0)
    else:
        print("⚠️ SOME SYSTEMS FAILED")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
