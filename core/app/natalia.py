
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
        self.role = "Beauty Sales Consultant"
        self.emoji_map = {"pricing": "💰", "location": "📍", "policy": "📋", "greeting": "✨"}
        # 💰 Estrategia VBO: Mapeo de valores estimados por servicio
        self.value_map = {
            "microblading": 300.0,
            "cejas": 250.0,
            "labios": 200.0,
            "ojos": 150.0,
            "general": 50.0
        }

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

        # 2. Context Retrieval (NEW: Maintain Context)
        from app.database import get_chat_history
        history = get_chat_history(phone, limit=5)
        
        # 3. Log User Message
        log_interaction(lead_id, "user", text)

        # 4. Context & Intent (Evolved with History)
        # TODO: Send 'history' to LLM for full contextual awareness.
        response_text = self._rule_based_response(text, history)

        # 5. Log Assistant Response
        log_interaction(lead_id, "assistant", response_text)
        
        # 6. Return execution plan (Controller will send message)
        return {
            "lead_id": lead_id,
            "reply": response_text,
            "action": "send_whatsapp"
        }

    def _rule_based_response(self, text: str, history: Optional[list] = None) -> str:
        """
        Versión Senior: Simulación de Neuro-Ventas basada en protocolos .ai
        """
        from app.database import get_knowledge_base
        
        text = text.lower()
        knowledge = get_knowledge_base()
        
        # 0. Context Awareness (Short Memory)
        if history and len(history) > 0:
            # Lógica de seguimiento si ya hubo charla
            pass

        # 1. Knowledge Retrieval & Injection
        # Buscamos en el 'business_knowledge' cargado en Supabase
        for fact in knowledge:
            if fact['category'] == 'pricing' and any(kw in text for kw in ['precio', 'costo', 'valor', 'cuanto']):
                if fact['slug'].split('_')[0] in text: # Ej: 'microblading'
                    return f"{self.emoji_map['greeting']} ¡Claro! {fact['content']}\n\nEs una inversión en tu rostro que dura meses. ¿Te gustaría agendar una evaluación gratuita para ver cómo quedaría en ti? 💖"

        # 2. Category Fallbacks (Tone: Professional & Warm)
        if any(kw in text for kw in ['donde', 'ubicacion', 'direccion']):
            loc = next((f['content'] for f in knowledge if f['category'] == 'location'), "Equipetrol.")
            return f"{self.emoji_map['location']} Estamos ubicados en {loc} ¿En qué zona te encuentras tú?"

        if any(kw in text for kw in ['cita', 'agenda', 'reserva', 'turno']):
            return "¡Me encantaría ayudarte a agendar! 📅 ¿Qué día de la semana te queda mejor para una evaluación gratuita con Jorge?"

        # 3. Default Greeting (Neuro-Sales Hook)
        return "¡Hola! Soy Natalia, asistente experta de Jorge Aguirre. ✨ ¿Estás lista para resaltar tu belleza natural hoy? ¿En qué servicio puedo asesorarte?"

# Singleton
natalia = NataliaBrain()
