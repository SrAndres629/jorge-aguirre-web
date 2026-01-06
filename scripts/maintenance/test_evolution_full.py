
import httpx
import asyncio
import os
import sys

# Full system test script

async def test_system():
    api_key = os.getenv("EVOLUTION_API_KEY", "B89599B2-37E4-4DCA-92D3-87F8674C7D69")
    evo_url = os.getenv("EVOLUTION_API_URL", "http://localhost:8081")
    web_url = "http://localhost:8000"
    n8n_url = "http://localhost:5678"
    
    print("🚀 Starting Comprehensive System Audit...\n")

    # 1. Web App Health
    print(f"🔹 Checking Web App ({web_url})...")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"{web_url}/health")
            if r.status_code == 200:
                print(f"   ✅ Healthy: {r.json()}")
            else:
                print(f"   ❌ Unhealthy: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"   ❌ Failed to connect: {e}")

    # 2. n8n Health
    print(f"\n🔹 Checking n8n ({n8n_url})...")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # n8n doesn't have a standard public /health endpoint enabled by default always, 
            # but /healthz usually works if configured, or just checking root.
            r = await client.get(f"{n8n_url}/healthz") 
            if r.status_code == 200:
                print(f"   ✅ Healthy: {r.json()}")
            else:
                 # Fallback check
                 r2 = await client.get(f"{n8n_url}/")
                 if r2.status_code == 200:
                     print(f"   ✅ Accesible (Dashboard loads)")
                 else:
                    print(f"   ❌ Unhealthy: {r.status_code}")
    except Exception as e:
        print(f"   ❌ Failed to connect: {e}")

    # 3. Evolution API
    print(f"\n🔹 Checking Evolution API ({evo_url})...")
    try:
        async with httpx.AsyncClient(headers={"apikey": api_key}, timeout=5.0) as client:
            r = await client.get(f"{evo_url}/instance/fetchInstances")
            if r.status_code == 200:
                instances = r.json()
                print(f"   ✅ API Accessible. Found {len(instances)} instances.")
                for i in instances:
                    name = i['instance']['instanceName']
                    status = i['instance']['status']
                    print(f"      - {name}: {status}")
                    
                    # Check Webhook
                    wh = await client.get(f"{evo_url}/webhook/find/{name}")
                    if wh.status_code == 200:
                        wd = wh.json()
                        print(f"        Webhook: {wd.get('url')} (Enabled: {wd.get('enabled')})")
            else:
                print(f"   ❌ Error: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"   ❌ Failed to connect: {e}")

    print("\n🏁 Audit Complete.")

if __name__ == "__main__":
    asyncio.run(test_system())
