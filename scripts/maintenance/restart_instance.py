
import asyncio
from scripts.maintenance.evolution_mcp.client import EvolutionClient

async def restart_and_trigger_sync():
    print("🔄 Restarting 'JorgeMain' to Trigger History Sync...")
    client = EvolutionClient()
    instance = "JorgeMain"
    
    try:
        # endpoint: /instance/restart/{instance}
        print("   Sending Restart Command...")
        result = await client.get(f"instance/restart/{instance}")
        print(f"   Result: {result}")
        
        # Wait for reconnection
        print("   Waiting 10s for reconnection...")
        await asyncio.sleep(10)
        
        state = await client.get(f"instance/connectionState/{instance}")
        print(f"   New State: {state}")
        
    except Exception as e:
        print(f"❌ Error restarting instance: {e}")

if __name__ == "__main__":
    asyncio.run(restart_and_trigger_sync())
