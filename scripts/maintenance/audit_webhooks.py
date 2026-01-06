
import asyncio
from scripts.maintenance.evolution_mcp.client import EvolutionClient

async def audit_webhooks():
    print("🕵️‍♂️ Auditing Evolution API Webhooks...")
    client = EvolutionClient()
    instance = "JorgeMain"
    
    try:
        # Check Webhook settings for the instance
        # Endpoint: /webhook/find/{instance}
        print(f"   Fetching webhook config for {instance}...")
        webhook = await client.get(f"webhook/find/{instance}")
        
        if isinstance(webhook, dict):
             enabled = webhook.get('enabled', False)
             url = webhook.get('url', 'Not Set')
             events = webhook.get('events', [])
             print(f"   ✅ Webhook Enabled: {enabled}")
             print(f"   🔗 URL: {url}")
             print(f"   found {len(events)} active events.")
             # print(events)
        else:
             print(f"   ⚠️ Webhook response undefined: {webhook}")

    except Exception as e:
        print(f"❌ Error checking webhooks: {e}")

if __name__ == "__main__":
    asyncio.run(audit_webhooks())
