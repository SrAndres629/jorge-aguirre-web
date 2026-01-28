
import logging
import google.generativeai as genai
from typing import Optional, Dict, Any, List
import asyncio
import time
from app.database import get_or_create_lead, log_interaction, get_chat_history, get_knowledge_base
from app.config import settings

# Import Tool Registry
from app.tools.registry import registry
from app.tools.definitions import * 

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
    COGNITIVE SINGULARITY (v4.0) - HYBRID AGENTIC VERSION
    Multi-Protocol AI Agent with Tool Use (Function Calling) Capabilities.
    """

    def __init__(self):
        self.model_name = 'models/gemini-pro' # Updated for better function calling support if available, or stay with flash
        # Note: 'gemini-pro' is often better for tools, but 'flash' is faster. Let's try flash first.
        self.model_name = 'models/gemini-1.5-flash' 
        
        self.generation_config = {
            "temperature": 0.4,
            "top_p": 0.95,
            "max_output_tokens": 8192,
        }
        
        self.safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]
        
        # Initialize Model
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=self.generation_config,
            safety_settings=self.safety_settings
        )

    async def _get_system_prompt(self, role: str, phone: str) -> str:
        """Dynamic Persona Injection based on sender role."""
        
        # 1. Fetch Knowledge for RAG (Retrieval-Augmented Generation)
        knowledge = await asyncio.to_thread(get_knowledge_base)
        knowledge_str = "\n".join([f"- {k['category'].upper()}: {k['content']}" for k in knowledge])

        base_personality = f"""
        Eres NATALIA, el Agente de Inteligencia Artificial de JORGE AGUIRRE FLORES.
        No eres un simple bot, eres un Agente Autónomo con capacidad de razonamiento.
        
        CONOCIMIENTO ACTUALIZADO:
        {knowledge_str}
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

        # DEFAULT: CLIENT PROTOCOL (Neuromarketing Level 99)
        return base_personality + """
        ESTADO: PROTOCOLO VENTAS PREMIUM (NEUROMARKETING).
        
        OBJETIVO:
        Convertir conversaciones en CITAS CONFIRMADAS mediante persuasión ética y alto valor percibido.
        
        TONO Y VOZ:
        - Eres NATURAL, no robótica. Escribes como una asistente de élite, no como un chat de soporte.
        - Usas emojis con elegancia (✨, 🤎, 👇), sin saturar.
        - Tus mensajes son cortos y directos ("Chunking"). Evita párrafos gigantes.
        - Usas NPL (Programación Neurolingüística): Palabras sensoriales (ver, sentir, lucir), anclajes positivos.
        
        TÉCNICAS DE NEUROMARKETING ACTIVAS:
        1. **Escasez Real**: "Nos quedan pocos cupos para esta semana".
        2. **Autoridad**: "El especialista Jorge Aguirre analiza cada rostro antes de..."
        3. **Prueba Social**: Menciona sutilmente que otras clientas están felices.
        
        REGLAS DE ORO:
        1. ⛔ PRECIOS: NUNCA des el precio solo. Siempre debe ir envuelto en el "Sandwich de Valor" (Beneficio -> Precio -> Pregunta de Cierre).
        2. 🕵️ DIAGNÓSTICO: Antes de vender, pregunta. "¿Ya te has hecho micropigmentación antes o es tu primera vez?".
        3. 🤝 HUMAN-IN-THE-LOOP: Si preguntan algo fuera de script (casos médicos, ofertas locas), di:
           "Entiendo perfectamente. Como tu caso es especial, voy a consultarlo directamente con Jorge Aguirre y te aviso en unos minutos. ¿Te parece bien?"
        4. 🎯 CIERRE: Termina cada mensaje con una pregunta que invite a responder (Doble Opción: "¿Prefieres mañana o la próxima semana?").
        
        HERRAMIENTAS: 
        Tienes acceso a herramientas para consultar fechas y precios. ÚSALAS cuando sea necesario.
        """

    async def process_message(self, phone: str, text: str, meta_data: Optional[dict] = None) -> Dict[str, Any]:
        """Agentic processing loop with role detection and tool usage."""
        
        clean_phone = "".join(filter(str.isdigit, phone))
        
        # 🔒 SECURITY SENTINEL (Anti-Prompt Injection)
        if self._is_unsafe_prompt(text):
            logger.warning(f"🚨 SECURITY ALERT: Prompt Injection detected form {clean_phone}: {text}")
            return {
                "lead_id": clean_phone,
                "reply": "Entiendo tu mensaje, pero mi programación se enfoca exclusivamente en la estética y agenda de Jorge Aguirre. ¿En qué puedo ayudarte sobre eso? ✨",
                "action": "send_whatsapp",
                "is_new_lead": False,
                "metadata": {"security_block": True}
            }

        # Determine Role
        role = "CLIENT"
        if clean_phone == ADMIN_PHONE: role = "ROOT"
        elif clean_phone == CHIEF_PHONE: role = "CHIEF"

        logger.info(f"🧠 Agent Logic Start (Hybrid) | Role: {role} | Phone: {clean_phone}")

        # 1. Lead Identification
        lead_id, is_new_lead = await asyncio.to_thread(get_or_create_lead, phone, meta_data)
        await asyncio.to_thread(log_interaction, lead_id, "user", text)

        # 2. Context Retrieval
        history_rows = await asyncio.to_thread(get_chat_history, phone, limit=15)
        
        # Prepare Conversation History for Gemini
        gemini_history = []
        for msg in history_rows:
            g_role = "user" if msg['role'] == 'user' else "model"
            gemini_history.append({"role": g_role, "parts": [msg['content'] or "..."]})

        # 3. Neural Inference (THE HYBRID LOOP)
        final_reply = ""
        
        try:
            # Set System Instruction
            system_instruction = await self._get_system_prompt(role, clean_phone)
            self.model._system_instruction = system_instruction # Hack: Set system prompt

            chat_session = self.model.start_chat(history=gemini_history)
            
            # PHASE 1: User Input -> Model (with Tools)
            logger.info(f"🧠 [THINKING] Phase 1: Reasoning with Tools...")
            
            # Send message with tools enabled
            # Note: In latest genai, we pass tools at model init or chat creation, 
            # OR typically at generation time. For 'start_chat', tools are often a property of the chat object or passed in get_response.
            # We'll attach tools to the chat session call.
            
            response = await chat_session.send_message_async(
                text,
                tools=registry.get_tools_for_gemini()
            )

            # PHASE 2: Tool Execution Loop (Max 3 turns)
            MAX_TURNS = 3
            for turn in range(MAX_TURNS):
                # Check for Function Calls (Multiple calls possible?)
                # Simplified: Handle first candidate's function calls
                
                part = response.candidates[0].content.parts[0]
                
                if part.function_call:
                    func_call = part.function_call
                    tool_name = func_call.name
                    tool_args = dict(func_call.args)
                    
                    logger.info(f"🛠️ [TOOL DETECTED] {tool_name} with args: {tool_args}")
                    
                    # Execute Tool
                    tool_result = registry.execute(tool_name, tool_args)
                    
                    logger.info(f"🧠 [THINKING] Phase {turn+2}: Analyzing Tool Output...")

                    # Send result back
                    response = await chat_session.send_message_async(
                        genai.protos.Part(
                            function_response=genai.protos.FunctionResponse(
                                name=tool_name,
                                response={"result": tool_result}
                            )
                        )
                    )
                else:
                    # No function call -> Final Text
                    final_reply = response.text
                    break
            
            if not final_reply:
                final_reply = response.text

            # 🛡️ Human-in-the-loop Trigger
            if role == "CLIENT" and any(x in final_reply.lower() for x in ["voy a consultar con jorge", "consultaré directamente"]):
                await self._trigger_chief_consultation(clean_phone, text)
                
        except Exception as e:
            logger.error(f"❌ Cognitive Failure: {e}")
            final_reply = "Disculpa, estoy teniendo un refresh en mi sistema de agenda. Dame un momento y te atiendo con la exclusividad que mereces. ✨"

        # 4. Log Assistant Output
        await asyncio.to_thread(log_interaction, lead_id, "assistant", final_reply)
        
        # Determine Metadata (VBO)
        intent = "general"
        val = 50.0
        if "cejas" in text.lower() or "micro" in text.lower():
            intent = "microblading"
            val = 300.0
        
        return {
            "lead_id": lead_id,
            "reply": final_reply,
            "action": "send_whatsapp",
            "is_new_lead": is_new_lead,
            "metadata": {"intent": intent, "value": val}
        }

    async def _trigger_chief_consultation(self, client_phone: str, client_message: str):
        """
        Envía un mensaje automático a Jorge Aguirre (CHIEF) para resolver una duda de cliente.
        """
        logger.info(f"📢 [CONSULTATION TRIGGERED] Request from {client_phone} sent to Chief.")
        
        from app.evolution import evolution_service
        consultation_msg = (
            f"🧠 *NATALIA - CONSULTA URGENTE*\n\n"
            f"Jorge, tengo una clienta con una duda que requiere tu criterio:\n\n"
            f"👤 *Cliente:* {client_phone}\n"
            f"💬 *Mensaje:* {client_message}\n\n"
            f"¿Cómo debería proceder? Respóndeme por aquí para que yo le informe."
        )
        if evolution_service:
            await evolution_service.send_text(CHIEF_PHONE, consultation_msg)

    def _is_unsafe_prompt(self, text: str) -> bool:
        """
        Detecta intentos básicos de manipulación de prompt.
        """
        text_lower = text.lower()
        forbidden_patterns = [
            "ignore previous instructions",
            "ignora las instrucciones",
            "you are now",
            "ahora eres",
            "system prompt",
            "tu prompt de sistema",
            "reveal your instructions",
            "modo desarrollador",
            "developer mode"
        ]
        return any(pattern in text_lower for pattern in forbidden_patterns)

# Singleton Instance
natalia = NataliaBrain()
