import httpx
import asyncio
import json

API_URL = "https://evolution-whatsapp-zn13.onrender.com"
API_KEY = "JorgeSecureKey123"

async def audit_instances():
    headers = {"apikey": API_KEY}
    print("🕵️ AUDITING EVOLUTION INSTANCES...")
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{API_URL}/instance/fetchInstances", headers=headers)
            print(f"Status: {resp.status_code}")
            
            if resp.status_code == 200:
                instances = resp.json()
                print(f"Found {len(instances)} instances.")
                print(json.dumps(instances, indent=2))
                
                # Check connection state for each
                for inst in instances:
                    name = inst.get("instance", {}).get("instanceName") or inst.get("name")
                    if name:
                        print(f"\nChecking State for: {name}")
                        s_resp = await client.get(f"{API_URL}/instance/connectionState/{name}", headers=headers)
                        print(f"  > {s_resp.json()}")
            else:
                print(f"Error: {resp.text}")
                
        except Exception as e:
            print(f"Fatal Error: {e}")

if __name__ == "__main__":
    asyncio.run(audit_instances())
