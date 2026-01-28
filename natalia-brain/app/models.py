from pydantic import BaseModel
from typing import Optional, Dict, Any

class TrackResponse(BaseModel):
    status: str
    event_id: str
    category: str

class LeadCreate(BaseModel):
    whatsapp_phone: str
    meta_lead_id: Optional[str] = None
    click_id: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None

class InteractionCreate(BaseModel):
    lead_id: str
    role: str
    content: str
