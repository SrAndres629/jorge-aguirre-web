
import logging
from typing import Optional, Dict, Any
from app.database import get_or_create_lead, log_interaction, get_cursor
from app.models import LeadStatus

logger = logging.getLogger("NataliaBrain")

class NataliaBrain:
    """
    Cerebro de la Asistente de IA (Natalia).
    Maneja el estado de la conversación y decide la siguiente acción.
    """

    def __init__(self):
        self.name = "Natalia"

    def process_message(self, phone: str, text: str, meta_data: Optional[dict] = None) -> Dict[str, Any]:
        """
        Procesa un mensaje entrante de WhatsApp.
        1. Identifica/Crea el Lead.
        2. Guarda el mensaje (User).
        3. Determina intención.
        4. Genera respuesta.
        5. Guarda respuesta (Assistant).
        """
        logger.info(f"🧠 Natalia Processing: {phone} - '{text}'")

        # 1. Lead Identification
        lead_id = get_or_create_lead(phone, meta_data)
        if not lead_id:
            return {"error": "Failed to identify lead"}

        # 2. Log User Message
        log_interaction(lead_id, "user", text)

        # 3. Context & Intent (Primitive V1)
        # TODO: Connect to LLM (Ollama/OpenAI) here.
        # For now, rule-based logic.
        response_text = self._rule_based_response(text)

        # 4. Log Assistant Response
        log_interaction(lead_id, "assistant", response_text)
        
        # 5. Return execution plan (Controller will send message)
        return {
            "lead_id": lead_id,
            "reply": response_text,
            "action": "send_whatsapp"
        }

    def _rule_based_response(self, text: str) -> str:
        text = text.lower()
        if "precio" in text or "costo" in text:
            return "Nuestros precios varían según el servicio. Microblading desde $150. ¿Te gustaría agendar una evaluación gratuita?"
        elif "agenda" in text or "cita" in text:
            return "¡Claro! ¿Qué día te queda mejor?"
        elif "ubicacion" in text or "donde" in text:
            return "Estamos en Equipetrol, Calle Tucumán #45."
        else:
            return "¡Hola! Soy Natalia. ¿En qué puedo ayudarte hoy para resaltar tu belleza?"

# Singleton
natalia = NataliaBrain()
