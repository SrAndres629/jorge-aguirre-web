
from ..client import EvolutionClient
from pydantic import BaseModel, Field

client = EvolutionClient()

async def set_webhook(url: str, enabled: bool, events: list, instance: str):
    payload = {
        "webhook": {
            "enabled": enabled,
            "url": url,
            "webhook_by_instance": True,
            "events": events
        }
    }
    return await client.post(f"webhook/set/{instance}", payload)

async def find_webhook(instance: str):
    return await client.get(f"webhook/find/{instance}")
