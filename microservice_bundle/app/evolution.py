
import httpx
import logging
from typing import List, Dict, Any, Optional
from app.config import settings

logger = logging.getLogger("EvolutionService")

class EvolutionService:
    """
    Servicio de integración Senior con Evolution API.
    Maneja el envío, recepción y recuperación de historial directamente desde el socket de WhatsApp.
    """
    def __init__(self):
        self.base_url = settings.EVOLUTION_API_URL.rstrip('/')
        self.api_key = settings.EVOLUTION_API_KEY
        self.instance = settings.EVOLUTION_INSTANCE

    async def send_text(self, phone: str, text: str) -> bool:
        """Envía un mensaje de texto simple"""
        url = f"{self.base_url}/message/sendText/{self.instance}"
        headers = {"apikey": self.api_key}
        # Aseguramos formato internacional sin el + pero con el código de país
        clean_phone = "".join(filter(str.isdigit, phone))
        
        payload = {
            "number": clean_phone,
            "text": text,
            "linkPreview": True
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                resp = await client.post(url, json=payload, headers=headers)
                resp.raise_for_status()
                logger.info(f"📤 Mensaje enviado a {clean_phone} via Evolution")
                return True
            except Exception as e:
                logger.error(f"❌ Error enviando mensaje via Evolution: {e}")
                return False

    async def fetch_history(self, phone: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Recupera el historial de mensajes directamente desde el servidor de Evolution.
        Útil para dar contexto a Natalia cuando la DB local está vacía.
        """
        url = f"{self.base_url}/chat/fetchMessages/{self.instance}"
        headers = {"apikey": self.api_key}
        clean_phone = "".join(filter(str.isdigit, phone))
        params = {"number": clean_phone, "limit": limit}

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                resp = await client.get(url, params=params, headers=headers)
                resp.raise_for_status()
                messages = resp.json()
                # Evolution suele devolver una lista de mensajes en formato oficial de WA
                return messages if isinstance(messages, list) else []
            except Exception as e:
                logger.warning(f"⚠️ No se pudo recuperar historial de Evolution para {phone}: {e}")
                return []

    async def get_instance_status(self) -> Dict[str, Any]:
        """Verifica si la instancia está conectada (Self-Healing Check)"""
        url = f"{self.base_url}/instance/connectionState/{self.instance}"
        headers = {"apikey": self.api_key}
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                resp = await client.get(url, headers=headers)
                return resp.json()
            except Exception as e:
                return {"instance": self.instance, "status": "error", "message": str(e)}

# Export Singleton
evolution_service = EvolutionService()
