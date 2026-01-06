
import asyncio
import json
from scripts.maintenance.evolution_mcp.client import EvolutionClient
from scripts.maintenance.evolution_mcp.tools import instances

async def audit_instances():
    print("🕵️‍♂️ Auditing Evolution API Instances...")
    
    client = EvolutionClient()
    
    try:
        # Use Client directly to get full instances info
        result = await client.get("instance/fetchInstances")
        
        if isinstance(result, list):
            insts = result
        else:
             insts = result.get('data', [])

        print(f"📋 Found {len(insts)} instances.")
        
        for inst in insts:
            # Handle different response structures
            if isinstance(inst, dict):
                 name = inst.get('instance', {}).get('instanceName') or inst.get('name')
                 status = inst.get('instance', {}).get('status') or inst.get('status')
            else:
                 name = str(inst)
                 status = "Unknown"

            print(f"\n🔍 Instance: {name} | Status: {status}")
            
            if name:
                # Check Settings for this instance
                print(f"   Getting settings for {name}...")
                settings_res = await client.get(f"settings/find/{name}")
                # Evolution v2 settings structure usually has 'settings' key
                # We specifically look for 'store_messages'
                
                if isinstance(settings_res, dict):
                     # print(json.dumps(settings_res, indent=2)) 
                     # Check common config paths
                     chat_settings = settings_res.get('chat', {})
                     store_msgs = chat_settings.get('archive', {}).get('status') # Old v1?
                     # Try finding 'store'
                     print(f"   Settings Dump: {json.dumps(settings_res, indent=2)}")

    except Exception as e:
        print(f"❌ Error during audit: {e}")

if __name__ == "__main__":
    asyncio.run(audit_instances())
