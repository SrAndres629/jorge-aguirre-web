# =================================================================
# MODELS.PY - Pydantic Schemas para validación de requests
# Jorge Aguirre Flores Web
# =================================================================
from pydantic import BaseModel, Field
from typing import Optional


class LeadTrackRequest(BaseModel):
    """Schema para POST /track-lead"""
    event_id: str = Field(..., description="ID único del evento para deduplicación")
    source: str = Field(..., description="Fuente del lead (ej: 'Hero CTA', 'Floating Button')")


class ViewContentRequest(BaseModel):
    """Schema para POST /track-viewcontent"""
    service: str = Field(..., description="Nombre del servicio visto")
    category: str = Field(..., description="Categoría del servicio (cejas, ojos, labios)")
    price: Optional[float] = Field(default=0, description="Precio del servicio en USD")


class VisitorResponse(BaseModel):
    """Response schema para visitantes"""
    id: int
    external_id: str
    fbclid: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    source: Optional[str] = None
    timestamp: Optional[str] = None


class HealthResponse(BaseModel):
    """Response schema para /health"""
    status: str
    database: str
    timestamp: str
    service: str


class TrackResponse(BaseModel):
    """Response genérico para endpoints de tracking"""
    status: str
    event_id: Optional[str] = None
    category: Optional[str] = None


class ConfirmSaleResponse(BaseModel):
    """Response para POST /admin/confirm/{visitor_id}"""
    status: str
    visitor_id: int
    value: float
    event_id: str


class ErrorResponse(BaseModel):
    """Response para errores"""
    status: str = "error"
    error: str
