
from ..client import EvolutionClient

client = EvolutionClient()

# --- Groups ---
async def create_group(subject: str, participants: list, instance: str):
    payload = {"subject": subject, "participants": participants}
    return await client.post(f"group/create/{instance}", payload)

async def update_group_subject(group_jid: str, subject: str, instance: str):
    payload = {"subject": subject}
    return await client.post(f"group/updateSubject/{instance}?groupJid={group_jid}", payload)

# --- Contacts ---
async def check_number(number: str, instance: str):
    """Check if number exists on WhatsApp"""
    return await client.post(f"chat/checkNumber/{instance}", {"numbers": [number]})

async def block_contact(number: str, instance: str, block: bool = True):
    endpoint = "block" if block else "unblock"
    payload = {"number": number}
    return await client.post(f"chat/{endpoint}/{instance}", payload)

async def get_profile_pic(number: str, instance: str):
    return await client.post(f"chat/fetchProfilePictureUrl/{instance}", {"number": number})
