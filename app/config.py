# =================================================================
# CONFIG.PY - Configuración centralizada con validación
# Jorge Aguirre Flores Web
# =================================================================
import os
from typing import Optional
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Settings:
    """Configuración centralizada del sistema con validación"""
    
    def __init__(self):
        # Meta Ads (Pixel + CAPI)
        self.META_PIXEL_ID: str = os.getenv("META_PIXEL_ID", "1412977383680793")
        self.META_ACCESS_TOKEN: str = os.getenv(
            "META_ACCESS_TOKEN",
            "EAAmeW8lDnZAQBQJ61ZC4CCfcNFZBZAQuFBJE06SOZB1AvAexCyUVY3ajvW9u46dvMoYvFMSudqhdYNW4A2PQicr0tcUZBG0itr9ZBUZAuzq7eC83avJT9ox75W5WrncNheJ928IZAo4BxB403x8eeckpdYU8dgu84pHxZC0lEVssgLWWE1Xm30JZCuQbKKkoZB2dkgZDZD"
        )
        self.META_API_VERSION: str = "v21.0"
        self.TEST_EVENT_CODE: Optional[str] = os.getenv("TEST_EVENT_CODE")
        
        # Database (Supabase PostgreSQL)
        self.DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
        
        # Admin Panel
        self.ADMIN_KEY: str = os.getenv("ADMIN_KEY", "Andromeda2025")
        
        # Server
        self.HOST: str = os.getenv("HOST", "0.0.0.0")
        self.PORT: int = int(os.getenv("PORT", "8000"))
        
        # WhatsApp
        self.WHATSAPP_NUMBER: str = os.getenv("WHATSAPP_NUMBER", "59176375924")
        
        self._validate()
    
    def _validate(self):
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
