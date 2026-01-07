# =================================================================
# CONFIG.PY - Configuración centralizada con validación (Pydantic)
# Jorge Aguirre Flores Web
# =================================================================
import os
from typing import Optional
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
    
    # Database (Supabase PostgreSQL)
    DATABASE_URL: Optional[str] = None
    
    # Celery & Redis
    CELERY_BROKER_URL: str = "redis://redis_evolution:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://redis_evolution:6379/1"
    
    # Admin Panel
    ADMIN_KEY: str = os.getenv("ADMIN_KEY", "Andromeda2025")
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # WhatsApp / Evolution API
    WHATSAPP_NUMBER: str = "59164714751"
    EVOLUTION_API_KEY: Optional[str] = None
    EVOLUTION_API_URL: str = "http://evolution_api:8080"

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
