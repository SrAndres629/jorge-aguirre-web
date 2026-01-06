
import asyncio
from scripts.maintenance.evolution_mcp.client import EvolutionClient

async def fix_settings():
    print("🛠️ Fixing Evolution API Settings for 'JorgeMain'...")
    
    client = EvolutionClient()
    instance = "JorgeMain"
    
    # 1. Update Settings to ensure history is synced and instance stays online
    payload = {
        "rejectCall": False,
        "groupsIgnore": False,
        "alwaysOnline": True,
        "readMessages": False,
        "readStatus": False,
        "syncFullHistory": True
    }
    
    try:
        print(f"   Sending update to /settings/set/{instance}...")
        result = await client.post(f"settings/set/{instance}", payload)
        print(f"   Result: {result}")
        
        # 2. Check Connection Status
        print(f"   Checking status...")
        status = await client.get(f"instance/connectionState/{instance}")
        print(f"   Status: {status}")
        
    except Exception as e:
        print(f"❌ Error updating settings: {e}")

if __name__ == "__main__":
    asyncio.run(fix_settings())
