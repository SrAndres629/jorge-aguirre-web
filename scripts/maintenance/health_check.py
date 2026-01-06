
import asyncio
import logging
from typing import Dict, Any
from scripts.maintenance.evolution_mcp.client import EvolutionClient
import socket

# Setup Logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("HealthCheck")

class SystemAuditor:
    def __init__(self):
        self.client = EvolutionClient()
        self.instance = "JorgeMain"

    async def check_api_connectivity(self) -> bool:
        """1. Basic API Ping"""
        try:
            # Try fetch instances as ping
            await self.client.get("instance/fetch")
            logger.info("✅ API Connectivity: ONLINE")
            return True
        except Exception as e:
            logger.error(f"❌ API Connectivity: DOWN ({e})")
            return False

    async def check_instance_state(self) -> bool:
        """2. Instance 'JorgeMain' Status"""
        try:
            state = await self.client.get(f"instance/connectionState/{self.instance}")
            # Format usually: {'instance': {'state': 'open'}}
            status = state.get('instance', {}).get('state') or state.get('state')
            
            if status == 'open':
                logger.info(f"✅ Instance '{self.instance}': CONNECTED (open)")
                return True
            else:
                logger.warning(f"⚠️ Instance '{self.instance}': {status} (Expected: open)")
                return False
        except Exception as e:
            logger.error(f"❌ Instance Check Error: {e}")
            return False

    async def check_webhook_config(self) -> bool:
        """3. Webhook Configuration Validity"""
        try:
            config = await self.client.get(f"webhook/find/{self.instance}")
            
            url = config.get('url')
            enabled = config.get('enabled')
            by_events = config.get('webhookByEvents')
            
            checks = []
            
            if enabled:
                checks.append("✅ Enabled")
            else:
                checks.append("❌ DISABLED")
                
            if url == "http://n8n:5678/webhook/website-events-v2":
                checks.append("✅ URL Correct")
            else:
                checks.append(f"❌ URL Mismatch ({url})")
                
            if not by_events:
                checks.append("✅ Single URL Mode (Correct)")
            else:
                checks.append("❌ Event Splitting ON (Incorrect)")
                
            logger.info(f"Webhook Status: {', '.join(checks)}")
            
            return enabled and (not by_events)
            
        except Exception as e:
            logger.error(f"❌ Webhook Check Error: {e}")
            return False

    def check_n8n_port(self) -> bool:
        """4. Check if n8n port is open locally (container-to-container simulation)"""
        # Since we run this from host, we check localhost:5678
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 5678))
        sock.close()
        if result == 0:
            logger.info("✅ n8n Port (5678): OPEN")
            return True
        else:
            logger.error("❌ n8n Port (5678): CLOSED")
            return False

    async def run_audit(self):
        print("\n🦅 EXTENSIVE SYSTEM HEALTH AUDIT (Protocol Jorge Aguirre)\n" + "="*60)
        
        c1 = await self.check_api_connectivity()
        if not c1:
            print("\n❌ CRITICAL: API is unreachable. Aborting.")
            return

        c2 = await self.check_instance_state()
        c3 = await self.check_webhook_config()
        c4 = self.check_n8n_port()
        
        print("="*60)
        if c1 and c2 and c3 and c4:
            print("🟢 SYSTEM STATUS: 100% OPERATIONAL")
            print("   (Ready for Production Usage)")
        else:
            print("⚠️ SYSTEM STATUS: DEGRADED")
            print("   Review logs above for specific failures.")

if __name__ == "__main__":
    auditor = SystemAuditor()
    asyncio.run(auditor.run_audit())
