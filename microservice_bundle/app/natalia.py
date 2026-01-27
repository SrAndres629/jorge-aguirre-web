
import logging
import google.generativeai as genai
from typing import Optional, Dict, Any, List
from app.database import get_or_create_lead, log_interaction, get_cursor, get_chat_history
from app.config import settings

# Configure Logger
logger = logging.getLogger("NataliaBrain")

# Roles & Identities
ADMIN_PHONE = "59178113055"  # Root / Developer
CHIEF_PHONE = "59176863944"  # Jorge Aguirre (Esteticista Jefe)

if settings.GOOGLE_API_KEY:
    genai.configure(api_key=settings.GOOGLE_API_KEY)
else:
    logger.critical("🚨 GOOGLE_API_KEY missing! Brain functionality disabled.")

class NataliaBrain:
    """
    COGNITIVE SINGULARITY (v3.0) - AGENTIC VERSION
    Multi-Protocol AI Agent with Human-in-the-loop capability.
    Handles 3 classes of chats: ROOT (Dev), CHIEF (Business), CLIENT (Leads).
    """

    def __init__(self):
        self.model_name = 'models/gemini-flash-latest'
        self.generation_config = {
            "temperature": 0.4, # Lowered for consistency in agentic behavior
            "top_p": 0.95,
            "max_output_tokens": 8192,
        }
        
        self.safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]

    def _get_system_prompt(self, role: str, phone: str) -> str:
        """Dynamic Persona Injection based on sender role."""
        
        base_personality = """
        Eres NATALIA, el Agente de Inteligencia Artificial de JORGE AGUIRRE FLORES.
        No eres un simple bot, eres un Agente Autónomo con capacidad de razonamiento.
        """

        if role == "ROOT":
            return base_personality + f"""
            ESTADO: PROTOCOLO ROOT ACTIVADO.
            USUARIO: {phone} (Desarrollador / Admin del Sistema).
            REGLAS:
            - Tienes acceso total. Si te pide métricas, historial o cambios en el sistema, dile que "Procederás con las herramientas de Agente".
            - Puedes discutir arquitectura, opiniones de campañas y programar mensajes.
            - Responde con tono de 'Compañero de Inteligencia' profesional y técnico.
            """
            
        if role == "CHIEF":
            return base_personality + f"""
            ESTADO: PROTOCOLO JEFE (ESTETICISTA) ACTIVADO.
            USUARIO: {phone} (Jorge Aguirre Flores).
            REGLAS:
            - Eres su mano derecha. Jorge es la autoridad técnica.
            - Si te da una instrucción (ej: 'Hoy hay 10% de descuento'), guárdalo en tu contexto y aplícalo a todos los clientes futuros.
            - Reporta resúmenes de clientas si te lo pide.
            - Responde con tono servicial, eficiente y de alta gama.
            """

        # DEFAULT: CLIENT PROTOCOL
        return base_personality + """
        ESTADO: PROTOCOLO ATENCIÓN AL CLIENTE.
        SERVICIOS: Microblading ($215), Labios ($170), Ojos ($145).
        REGLAS:
        1. PERSUASIÓN: Nunca des precios sin valor previo.
        2. DIAGNÓSTICO: Pregunta siempre si tienen trabajo previo.
        3. HUMAN-IN-THE-LOOP: Si preguntan algo que NO sabes (ofertas especiales, casos médicos complejos, descuentos específicos), NO INVENTES. 
           Di: "Entiendo perfectamente tu solicitud. Como tu caso es especial, voy a consultarlo directamente con Jorge Aguirre en este momento y te avisaré apenas me responda. ¿Te parece bien?"
        4. ACCION: Si detectas que debes consultar al Jefe, el sistema te proporcionará una herramienta interna.
        """

    def process_message(self, phone: str, text: str, meta_data: Optional[dict] = None) -> Dict[str, Any]:
        """Agentic processing loop with role detection."""
        
        # Clean phone for comparison
        clean_phone = "".join(filter(str.isdigit, phone))
        
        # Determine Role
        role = "CLIENT"
        if clean_phone == ADMIN_PHONE: role = "ROOT"
        elif clean_phone == CHIEF_PHONE: role = "CHIEF"

        logger.info(f"🧠 Agent Logic Start | Role: {role} | Phone: {clean_phone}")

        # 1. Lead/User Identification
        lead_id, is_new_lead = get_or_create_lead(phone, meta_data)
        log_interaction(lead_id, "user", text)

        # 2. Context Retrieval
        history_rows = get_chat_history(phone, limit=15) 
        
        # 3. Neural Inference
        try:
            response_text = self._generate_thought(text, history_rows, role, clean_phone)
            
            # 🛡️ PROTOCOLO DE CONSULTA (HUMAN-IN-THE-LOOP - SIMULATED FOR NOW)
            # Detectar si el Agente decidió que debe consultar al jefe
            if role == "CLIENT" and any(x in response_text.lower() for x in ["voy a consultar con jorge", "consultaré directamente"]):
                self._trigger_chief_consultation(clean_phone, text)
                
        except Exception as e:
            logger.error(f"❌ Cognitive Failure: {e}")
            response_text = "Disculpa, estoy teniendo un refresh en mi sistema de agenda. Dame un momento y te atiendo con la exclusividad que mereces. ✨"

        # 4. Log Assistant Output
        log_interaction(lead_id, "assistant", response_text)
        
        return {
            "lead_id": lead_id,
            "reply": response_text,
            "role": role,
            "metadata": {"role": role}
        }

    def _generate_thought(self, user_text: str, history_rows: List[Dict], role: str, phone: str) -> str:
        model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=self.generation_config,
            safety_settings=self.safety_settings,
            system_instruction=self._get_system_prompt(role, phone)
        )
        
        gemini_history = []
        for msg in history_rows:
            g_role = "user" if msg['role'] == 'user' else "model"
            gemini_history.append({"role": g_role, "parts": [msg['content'] or "..."]})
            
        chat = model.start_chat(history=gemini_history)
        response = chat.send_message(user_text)
        return response.text.strip()

    def _trigger_chief_consultation(self, client_phone: str, client_message: str):
        """
        Envía un mensaje automático a Jorge Aguirre (CHIEF) para resolver una duda de cliente.
        """
        logger.info(f"📢 [CONSULTATION TRIGGERED] Request from {client_phone} sent to Chief.")
        
        # Import dynamic to avoid circular dependencies
        try:
            from app.evolution import evolution_service
            consultation_msg = (
                f"🧠 *NATALIA - CONSULTA URGENTE*\n\n"
                f"Jorge, tengo una clienta con una duda que requiere tu criterio:\n\n"
                f"👤 *Cliente:* {client_phone}\n"
                f"💬 *Mensaje:* {client_message}\n\n"
                f"¿Cómo debería proceder? Respóndeme por aquí para que yo le informe."
            )
            # Solo activa enviarlo si evolution_service está listo
            if evolution_service:
                evolution_service.send_text(CHIEF_PHONE, consultation_msg)
        except Exception as e:
            logger.error(f"⚠️ Failed to send consultation to Chief: {e}")

# Singleton Instance
natalia = NataliaBrain()
