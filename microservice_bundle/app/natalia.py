
import logging
import google.generativeai as genai
from typing import Optional, Dict, Any, List
from app.database import get_or_create_lead, log_interaction, get_cursor, get_chat_history
from app.config import settings

# Configure Logger & AI
logger = logging.getLogger("NataliaBrain")

if settings.GOOGLE_API_KEY:
    genai.configure(api_key=settings.GOOGLE_API_KEY)
else:
    logger.critical("🚨 GOOGLE_API_KEY missing! Brain functionality disabled.")

class NataliaBrain:
    """
    COGNITIVE SINGULARITY (v2.0)
    Asistente Inteligente Probabilístico con Memoria Contextual.
    Powered by Google Gemini 1.5 Flash.
    """

    def __init__(self):
        # Modelo Ganador (Confirmado por Script de Auditoría)
        self.model_name = 'models/gemini-flash-latest'
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }
        
        # 🛡️ Safety Settings (Permissive for sales, blockers for hate/harassment)
        self.safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]
        
        # 💰 VBO Estimator Map
        self.value_map = {
            "curso": 500.0,
            "microblading": 300.0,
            "cejas": 250.0,
            "labios": 200.0,
            "ojos": 150.0,
            "general": 50.0
        }
        
        self.junk_keywords = ["spam", "publicidad", "vendedor", "banco", "crédito"]

    def _get_system_prompt(self) -> str:
        """The Cognitive Core: Persona, Strategy & Knowledge Base."""
        return """
        Eres NATALIA, Asistente Expert y Estratega de Ventas de JORGE AGUIRRE FLORES (Maestro Internacional en Maquillaje Permanente).
        
        TUS SERVICIOS & PRECIOS (Referencia USD/BOB):
        - Microblading / Cejas Pelo a Pelo: 1500 Bs / $215 USD (Dura hasta 2 años).
        - Labios Full Color / Aquarelle: 1200 Bs / $170 USD.
        - Delineado de Ojos: 1000 Bs / $145 USD.
        - Correcciones de trabajos anteriores: Varía según complejidad (requiere evaluación).
        
        TU ESTILO:
        - Profesional, empática, persuasiva pero honesta.
        - Usas emojis sutiles para dar calidez (✨, 👁️, 📅).
        - Respuestas concisas, optimizadas para lectura rápida en WhatsApp.
        
        REGLA DE ORO (VENTA CONSULTIVA):
        - NUNCA des el precio crudo sin antes comunicar el VALOR o hacer una pregunta de diagnóstico.
        - Si preguntan "¿Cuánto cuesta?", responde explicando brevemente los beneficios (duración, naturalidad, seguridad) y LUEGO da el rango de precios.
        - INDAGA SIEMPRE: "¿Es tu primera vez o tienes algún trabajo anterior?". Esto es vital para saber si es corrección.
        
        TU OBJETIVO:
        - Educar al cliente sobre la calidad Premium de Jorge Aguirre.
        - Llevar la conversación hacia agendar una 'Valoración Gratuita' (presencial o por fotos) para dar el precio exacto.
        - Ubicación: Equipetrol Norte, Santa Cruz (Zona Exclusiva).
        """

    def process_message(self, phone: str, text: str, meta_data: Optional[dict] = None) -> Dict[str, Any]:
        """
        Main cognitive loop: Input -> Context Injection -> Inference -> Output
        """
        logger.info(f"🧠 Cognitive Cycle Start: {phone}")

        # 1. Lead Identification
        lead_id, is_new_lead = get_or_create_lead(phone, meta_data)
        if not lead_id:
            return {"error": "Failed to identify lead"}

        if is_new_lead:
            logger.info(f"🎯 [SIGNAL] New Lead Detected: {phone}")

        # 2. Log User Input (Short-term memory acquisition)
        log_interaction(lead_id, "user", text)

        # 3. Context Retrieval (Long-term memory recall)
        # Fetch last 10 messages for immediate context awareness
        history_rows = get_chat_history(phone, limit=10) 
        
        # 4. Neural Inference (The Thinking Process)
        try:
            if not settings.GOOGLE_API_KEY:
                raise ValueError("Brain offline: API Key missing")
                
            response_text = self._generate_thought(text, history_rows)
            
        except Exception as e:
            # 🛡️ CIRCUIT BREAKER: Fallback to safe mode
            logger.error(f"❌ Cognitive Failure (Circuit Breaker Triggered): {e}")
            response_text = "En este momento estoy verificando la disponibilidad de la agenda con el sistema central. ¿Podrías aguardarme unos minutos? 🙏"

        # 5. Intent Analysis (Heuristic Support)
        intent = "general"
        val = 50.0
        lower_text = text.lower()
        if "cejas" in lower_text or "micro" in lower_text:
            intent = "microblading"
            val = 300.0
        elif "labios" in lower_text:
            intent = "labios"
            val = 200.0
        
        is_junk = any(kw in lower_text for kw in self.junk_keywords)

        # 6. Log Assistant Output
        log_interaction(lead_id, "assistant", response_text)
        
        return {
            "lead_id": lead_id,
            "reply": response_text,
            "action": "send_whatsapp",
            "is_new_lead": is_new_lead,
            "metadata": {
                "intent": intent,
                "value": val,
                "currency": "USD",
                "is_junk": is_junk
            }
        }

    def _generate_thought(self, user_text: str, history_rows: List[Dict]) -> str:
        """
        Constructs the context vector and queries the LLM.
        """
        model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=self.generation_config,
            safety_settings=self.safety_settings,
            system_instruction=self._get_system_prompt()
        )
        
        # Build Chat Session with History
        gemini_history = []
        
        # Transform DB history to Gemini format
        # DB returns recent-last (chronological reverse in SQL usually, but let's trust get_chat_history implementation)
        # get_chat_history returns: [{'role': 'user', 'content': 'hi'}]
        # Gemini expects roles: 'user' or 'model'
        for msg in history_rows:
            role = "user" if msg['role'] == 'user' else "model"
            # Filter empty content to avoid API errors
            content = msg['content'] or "..."
            gemini_history.append({"role": role, "parts": [content]})
            
        chat = model.start_chat(history=gemini_history)
        
        # Execute Inference
        response = chat.send_message(user_text)
        return response.text.strip()

# Singleton Instance
natalia = NataliaBrain()
