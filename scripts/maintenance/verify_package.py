
import sys
import os

# Ensure package is on path
sys.path.append(os.getcwd())

try:
    print("⏳ Importing Evolution MCP Client...")
    from scripts.maintenance.evolution_mcp.client import EvolutionClient
    from tenacity import retry
    print("✅ Tenacity import successful.")
    
    print("⏳ Importing Evolution MCP Tools...")
    from scripts.maintenance.evolution_mcp.tools import messaging, instances, social, webhooks
    
    print("✅ API Structure Verified: All modules imported successfully.")
    
    client = EvolutionClient()
    if client.base_url:
         print("✅ Client Configuration Verified.")
         print(f"   URL: {client.base_url}")
         # Key should be masked
         key_status = "SET" if client.headers.get("apikey") else "MISSING"
         print(f"   API Key: {key_status}")
    else:
         print("❌ Client Configuration Failed.")
         sys.exit(1)

except ImportError as e:
    print(f"❌ Import Error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected Error: {e}")
    sys.exit(1)
