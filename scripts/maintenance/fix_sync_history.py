
import asyncio
from scripts.maintenance.evolution_mcp.client import EvolutionClient

async def fix_settings():
    print("🔧 Fixing Instance Settings...")
    client = EvolutionClient()
    instance = "JorgeMain"
    
    payload = {
        "rejectCall": True,
        "msgCall": "No acepto llamadas. Por favor escribe tu mensaje.",
        "groupsIgnore": False,
        "alwaysOnline": True,
        "readMessages": True,
        "readStatus": True,
        "syncFullHistory": True
    }
    
    try:
        # endpoint: /settings/set/{instance}
        result = await client.post(f"settings/set/{instance}", payload)
        print(f"   Result: {result}")
        
    except Exception as e:
        print(f"❌ Error fixing settings: {e}")

if __name__ == "__main__":
    asyncio.run(fix_settings())
