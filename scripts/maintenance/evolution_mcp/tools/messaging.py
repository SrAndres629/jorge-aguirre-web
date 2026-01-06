
from mcp.server.fastmcp import Context
from client import EvolutionClient
from pydantic import BaseModel, Field, field_validator
import re

client = EvolutionClient()

# --- Models ---
class PhoneMessage(BaseModel):
    number: str = Field(..., description="Phone number (e.g., 59164714751)")
    text: str = Field(..., min_length=1)
    
    @field_validator('number')
    def validate_phone(cls, v):
        cleaned = re.sub(r'[+\-\s]', '', v)
        if not re.match(r"^\d{8,15}$", cleaned):
            raise ValueError(f"Invalid format: {v}")
        return cleaned

class MediaMessage(BaseModel):
    number: str
    media_type: str = Field(..., pattern="^(image|video|audio|document)$")
    media_url: str
    caption: str = ""
    
# --- Logic ---

async def send_text(number: str, text: str, instance: str):
    """Logic to send text"""
    try:
        model = PhoneMessage(number=number, text=text)
    except ValueError as e:
        return {"error": True, "message": str(e)}
        
    return await client.post(f"message/sendText/{instance}", model.model_dump())

async def send_media(number: str, media_type: str, url: str, caption: str, instance: str):
    """Logic to send media"""
    payload = {
        "number": number,
        "mediatype": media_type,
        "mimetype": f"{media_type}/mp4" if media_type == "video" else f"{media_type}/png", # Simplified, production should detect
        "caption": caption,
        "media": url
    }
    return await client.post(f"message/sendMedia/{instance}", payload)
