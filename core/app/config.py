# =================================================================
# CONFIG.PY - Configuración centralizada con validación (Pydantic)
# Jorge Aguirre Flores Web
# =================================================================
import os
from typing import Optional, List, Union
from pydantic import field_validator
import logging
from pydantic_settings import BaseSettings, SettingsConfigDict

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Configuración centralizada del sistema con validación"""
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

    # Meta Ads (Pixel + CAPI)
    META_PIXEL_ID: str = ""
    META_ACCESS_TOKEN: Optional[str] = None
    META_API_VERSION: str = "v21.0"
    TEST_EVENT_CODE: Optional[str] = None
    META_SANDBOX_MODE: bool = False # 🛡️ True = No enviar eventos reales a Meta
    
    # Security: CORS Origins
    BACKEND_CORS_ORIGINS: List[str] = [
        "https://jorgeaguirreflores.com",
        "https://www.jorgeaguirreflores.com",
        "https://jorge-aguirre-web.onrender.com",
        "http://localhost:8000",
        "http://localhost:5678"
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Database (Supabase PostgreSQL)
    DATABASE_URL: Optional[str] = None
    
    # Celery & Redis
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://redis_evolution:6379/1")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://redis_evolution:6379/1")
    CELERY_TASK_ALWAYS_EAGER: bool = False # Default to False, override via env var
    
    # Admin Panel
    ADMIN_KEY: str = os.getenv("ADMIN_KEY", "Andromeda2025")
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # WhatsApp / Evolution API
    WHATSAPP_NUMBER: str = "59164714751"
    EVOLUTION_API_KEY: Optional[str] = None
    EVOLUTION_API_URL: str = "http://evolution_api:8080"
    EVOLUTION_INSTANCE: str = "JorgeMain"

    # n8n Integration
    N8N_WEBHOOK_URL: str = "http://n8n:5678/webhook/website-events"
    
    def validate_critical(self):
        """Valida configuración crítica"""
        if not self.META_PIXEL_ID:
            logger.warning("⚠️ META_PIXEL_ID no configurado")
        if not self.META_ACCESS_TOKEN:
            logger.warning("⚠️ META_ACCESS_TOKEN no configurado")
        if not self.DATABASE_URL:
            logger.info("ℹ️ DATABASE_URL no configurado - DB deshabilitada")
        
        logger.info("✅ Configuración cargada correctamente")
    
    @property
    def meta_api_url(self) -> str:
        """URL completa para Meta CAPI"""
        return f"https://graph.facebook.com/{self.META_API_VERSION}/{self.META_PIXEL_ID}/events"
    
    @property
    def whatsapp_url(self) -> str:
        """URL de WhatsApp con número"""
        return f"https://wa.me/{self.WHATSAPP_NUMBER}"


# Singleton de configuración
settings = Settings()
settings.validate_critical()
