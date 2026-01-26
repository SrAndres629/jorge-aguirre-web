
import logging
from typing import Optional, Dict, Any
from app.database import get_or_create_lead, log_interaction, get_cursor
from app.evolution import evolution_service
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
            "curso": 500.0, # High Ticket Education
            "masterclass": 500.0,
            "microblading": 300.0,
            "pelo a pelo": 300.0,
            "cejas": 250.0,
            "shading": 250.0,
            "labios": 200.0,
            "aquarelle": 200.0,
            "ojos": 150.0,
            "delineado": 150.0,
            "remocion": 100.0,
            "general": 50.0
        }
        # 🛑 Pillar 4: Filtro Anti-Basura
        self.junk_keywords = [
            "spam", "ofensa", "insulto", "equivocado", "no me interesa", 
            "publicidad", "oferta", "busco trabajo", "vendedor"
        ]

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

        # 2. Context Retrieval
        from app.database import get_chat_history
        history = get_chat_history(phone, limit=5)
        
        # NOTE: Evolution API fallback removed - it was async and caused crash.
        # Local DB should always have history since we log every interaction.
        # TODO: Refactor to async if Evolution fallback is needed in future.
        
        # 3. Log User Message
        log_interaction(lead_id, "user", text)

        # 4. Context & Intent (Evolved with History)
        # TODO: Send 'history' to LLM for full contextual awareness.
        response_text = self._rule_based_response(text, history)

        # 5. Determine estimated value for VBO (Pillar 1)
        intent = "general"
        for key in self.value_map.keys():
            if key in text.lower():
                intent = key
                break
        value = self.value_map[intent]

        # Pillar 4: Detect Junk Signal
        is_junk = any(kw in text.lower() for kw in self.junk_keywords)
        if is_junk:
            logger.warning(f"🛑 [ANTI-JUNK] Negative intent detected for {phone}")

        # 6. Log Assistant Response
        log_interaction(lead_id, "assistant", response_text)
        
        # 7. Return execution plan (Controller will send message)
        return {
            "lead_id": lead_id,
            "reply": response_text,
            "action": "send_whatsapp",
            "metadata": {
                "intent": intent,
                "value": value,
                "currency": "USD",
                "is_junk": is_junk
            }
        }

    def _rule_based_response(self, text: str, history: Optional[list] = None) -> str:
        """
        Conversion Strategist Implementation: 
        1. Frame: Diagnostic Surgeon (High Status)
        2. Technique: Price Anchoring
        3. Closer: Scarcity / Micro-Agreement
        """
        from app.database import get_knowledge_base
        
        text = text.lower()
        knowledge = get_knowledge_base()
        
        # 🛡️ STATUS MANAGEMENT: Frame Controller
        is_first_message = not history or len(history) < 2

        # 1. Diagnostic Frame (Surgeon Protocol)
        if any(kw in text for kw in ['precio', 'costo', 'cuanto', 'valor']):
            # Price Anchoring Logic
            for fact in knowledge:
                service_slug = fact['slug'].split('_')[0]
                if service_slug in text:
                    base_price = self.value_map.get(service_slug, 300.0)
                    anchor_price = base_price * 2
                    return (
                        f"Entiendo perfectamente. El valor depende del estado actual de tu piel. 🧐\n\n"
                        f"Para que te des una idea: un procedimiento de corrección de trabajo previo (cuando vienen de otros lugares) "
                        f"suele iniciar en {anchor_price} USD debido a la complejidad técnica.\n\n"
                        f"Sin embargo, si tu piel está 'virgen' o lista para diseño nuevo, la inversión para {service_slug.capitalize()} es de solo {base_price} USD.\n\n"
                        f"Dime, ¿ya tienes algún trabajo previo o sería tu primera vez?"
                    )
            # General fallback for price
            return "El valor de nuestros servicios de alta gama varía según la complejidad. Para Jorge lo más importante es la seguridad de tu rostro. ¿Te gustaría que iniciemos con una breve evaluación de tu caso para darte el presupuesto exacto? ✨"

        # 2. Scarcity & Social Proof (Closing Protocol)
        if any(kw in text for kw in ['cita', 'agenda', 'reserva', 'turno', 'cuándo']):
            return (
                "Jorge tiene una agenda bastante solicitada por la exclusividad de su técnica. 📅\n\n"
                "Suelo tener espacios disponibles recién para dentro de 5-7 días, pero a veces hay cambios de último minuto.\n\n"
                "¿Prefieres horario de mañana o tarde para ver qué puedo rescatar para ti?"
            )

        # 3. Knowledge Injection (Informational)
        for fact in knowledge:
            if any(kw in text for kw in ['donde', 'ubicacion', 'direccion']):
                if fact['category'] == 'location':
                    return f"{self.emoji_map['location']} Estamos en la zona más exclusiva de Equipetrol. {fact['content']} ¿Desde qué zona nos escribes tú? ✨"

        # 4. Default Greeting (Frame: Diagnostic Expert)
        if is_first_message:
            return (
                "¡Hola! Soy Natalia, especialista en diseño de mirada de Jorge Aguirre. ✨\n\n"
                "He recibido tu interés. Para asesorarte con el estándar de calidad que manejamos, "
                "¿podrías decirme qué zona de tu rostro te gustaría potenciar hoy?"
            )

        return "Entiendo. Cuéntame un poco más sobre lo que buscas proyectar con tu diseño. ¿Buscas algo muy natural o un efecto más definido? 👁️"

# Singleton
natalia = NataliaBrain()
