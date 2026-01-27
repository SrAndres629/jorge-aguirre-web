
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
        Endpoint: POST /chat/findMessages/{instance}
        """
        url = f"{self.base_url}/chat/findMessages/{self.instance}"
        headers = {"apikey": self.api_key}
        clean_phone = "".join(filter(str.isdigit, phone))
        
        # Payload para Query<Message> (Prisma-like)
        # Asumiendo que 'where' con 'key' -> 'remoteJid' filtra por chat
        payload = {
            "where": {
                "key": {
                    "remoteJid": f"{clean_phone}@s.whatsapp.net"
                }
            },
            "take": limit,
            "orderBy": [
                {"messageTimestamp": "desc"}
            ]
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                resp = await client.post(url, json=payload, headers=headers)
                resp.raise_for_status()
                messages = resp.json()
                # Evolution suele devolver una lista de mensajes en formato oficial de WA
                return messages if isinstance(messages, list) else []
            except Exception as e:
                logger.warning(f"⚠️ No se pudo recuperar historial de Evolution para {phone}: {e}")
                return []

    async def create_instance(self, instance_name: str = None) -> bool:
        """Crea la instancia en Evolution API si no existe"""
        instance = instance_name or self.instance
        url = f"{self.base_url}/instance/create"
        headers = {"apikey": self.api_key}
        payload = {
            "instanceName": instance,
            "token": self.api_key, # Usando misma key como token de instancia por simplicidad
            "qrcode": True,
            "integration": "WHATSAPP-BAILEYS"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                resp = await client.post(url, json=payload, headers=headers)
                if resp.status_code == 201 or resp.status_code == 200:
                    logger.info(f"✅ Instancia {instance} creada exitosamente")
                    return True
                else:
                    logger.error(f"❌ Fallo al crear instancia: {resp.text}")
                    return False
            except Exception as e:
                logger.error(f"❌ Error creando instancia: {e}")
                return False

    async def connect_instance(self) -> Optional[str]:
        """
        Solicita la conexión y devuelve el QR en Base64 si es necesario.
        Si ya está conectada, devuelve None.
        """
        # Primero ver estado
        status = await self.get_instance_status()
        if status.get("instance") and status["instance"].get("state") == "open":
            logger.info("ℹ️ Instancia ya conectada")
            return None
            
        # Llamar a connect para obtener QR
        url = f"{self.base_url}/instance/connect/{self.instance}"
        headers = {"apikey": self.api_key}
        
        async with httpx.AsyncClient(timeout=20.0) as client:
            try:
                resp = await client.get(url, headers=headers)
                data = resp.json()
                # Evolution v2 suele devolver { "base64": "..." } o similar en el endpoint connect
                if "base64" in data:
                    return data["base64"]
                elif "qrcode" in data and "base64" in data["qrcode"]:
                     return data["qrcode"]["base64"]
                return None
            except Exception as e:
                logger.error(f"❌ Error obteniendo QR: {e}")
                return None

    async def get_instance_status(self) -> Dict[str, Any]:
        """Verifica si la instancia está conectada (Self-Healing Check)"""
        url = f"{self.base_url}/instance/connectionState/{self.instance}"
        headers = {"apikey": self.api_key}
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                resp = await client.get(url, headers=headers)
                # Parsear respuesta incluso si es 404 (para saber que no existe)
                if resp.status_code == 404:
                    return {"status": "processing", "message": "Instance not found"}
                return resp.json()
            except Exception as e:
                return {"instance": self.instance, "status": "error", "message": str(e)}

# Export Singleton
evolution_service = EvolutionService()
