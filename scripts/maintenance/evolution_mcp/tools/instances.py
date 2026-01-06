
from ..client import EvolutionClient

client = EvolutionClient()

async def get_status(instance: str):
    return await client.get(f"instance/connectionStatus/{instance}")

async def list_instances():
    return await client.get("instance/fetchInstances")

async def create_instance(instance_name: str, token: str = None):
    payload = {"instanceName": instance_name}
    if token:
        payload["token"] = token
    return await client.post("instance/create", payload)

async def delete_instance(instance: str):
    return await client.delete(f"instance/delete/{instance}")

async def restart_instance(instance: str):
    return await client.get(f"instance/restart/{instance}")

async def logout_instance(instance: str):
    return await client.delete(f"instance/logout/{instance}")
