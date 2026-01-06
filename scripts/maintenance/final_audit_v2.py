
import asyncio
import os
import sys
from scripts.maintenance.evolution_mcp.client import EvolutionClient

# Force colors for output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

async def audit_system():
    print(f"{Colors.HEADER}🔎 STARTING FINAL SYSTEM AUDIT (JORGE AGUIRRE PROTOCOL){Colors.ENDC}")
    client = EvolutionClient()
    instance = "JorgeMain"
    
    # 1. Check API Health
    print(f"\n{Colors.OKCYAN}1. API Connectivity Check...{Colors.ENDC}")
    try:
        # Evolution doesn't have a standard /health root, but we can list instances
        instances = await client.get("instance/fetch")
        if isinstance(instances, list):
             print(f"{Colors.OKGREEN}✅ API is reachable. Found {len(instances)} instances.{Colors.ENDC}")
        else:
             print(f"{Colors.WARNING}⚠️ API reachable but unexpected response format.{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}❌ API Unreachable: {e}{Colors.ENDC}")
        return

    # 2. Check Instance State
    print(f"\n{Colors.OKCYAN}2. Instance 'JorgeMain' Health...{Colors.ENDC}")
    try:
        state = await client.get(f"instance/connectionState/{instance}")
        # Response format usually: { "instance": "JorgeMain", "state": "open" }
        status = state.get('instance', {}).get('state') or state.get('state')
        
        if status == 'open':
            print(f"{Colors.OKGREEN}✅ Instance State: OPEN (Connected){Colors.ENDC}")
        elif status == 'connecting':
             print(f"{Colors.WARNING}⚠️ Instance State: CONNECTING (Wait for QR scan){Colors.ENDC}")
        else:
             print(f"{Colors.FAIL}❌ Instance State: {status} (Requires attention){Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}❌ Failed to get instance state: {e}{Colors.ENDC}")

    # 3. Check Settings (Data Sync)
    print(f"\n{Colors.OKCYAN}3. Configuration Audit (Sync & History)...{Colors.ENDC}")
    try:
        settings = await client.get(f"settings/find/{instance}")
        # Deep inspection of nested settings
        # API v2 usually returns { "settings": { ... } }
        conf = settings.get('settings', settings)
        
        sync_history = conf.get('sync_full_history') or conf.get('syncFullHistory')
        reject_calls = conf.get('reject_call') or conf.get('rejectCall')
        
        if sync_history:
             print(f"{Colors.OKGREEN}✅ syncFullHistory: ENABLED (Retrieving past chats){Colors.ENDC}")
        else:
             print(f"{Colors.FAIL}❌ syncFullHistory: DISABLED (Fix this for chat history){Colors.ENDC}")
             
    except Exception as e:
        print(f"{Colors.FAIL}❌ Failed to fetch settings: {e}{Colors.ENDC}")

    # 4. Webhook Audit
    print(f"\n{Colors.OKCYAN}4. Webhook Configuration (The 'Ears' of the AI)...{Colors.ENDC}")
    try:
        webhook = await client.get(f"webhook/find/{instance}")
        # format: { "enabled": true, "url": "...", "events": [...] }
        
        if webhook.get('enabled'):
             print(f"{Colors.OKGREEN}✅ Webhook: ENABLED{Colors.ENDC}")
             print(f"   🔗 URL: {webhook.get('url')}")
             
             events = webhook.get('events', [])
             required = ['MESSAGES_UPSERT', 'MESSAGES_UPDATE', 'SEND_MESSAGE', 'CONNECTION_UPDATE']
             missing = [req for req in required if req not in events]
             
             if not missing:
                 print(f"{Colors.OKGREEN}✅ Critical Events: ALL ACTIVE ({len(events)} total){Colors.ENDC}")
             else:
                 print(f"{Colors.FAIL}❌ Missing Critical Events: {missing}{Colors.ENDC}")
        else:
             print(f"{Colors.FAIL}❌ Webhook: DISABLED{Colors.ENDC}")

    except Exception as e:
        print(f"{Colors.FAIL}❌ Failed to check webhook: {e}{Colors.ENDC}")

    print(f"\n{Colors.HEADER}🏁 AUDIT COMPLETE{Colors.ENDC}")

if __name__ == "__main__":
    asyncio.run(audit_system())
