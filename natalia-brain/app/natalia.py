
import logging
import google.generativeai as genai
from typing import Optional, Dict, Any, List
import asyncio
import time
from app.database import get_or_create_lead, log_interaction, get_chat_history, get_knowledge_base, get_agent_prompt
from app.config import settings
from app.roles import Role

# Import Tool Registry
from app.tools.registry import registry
from app.tools.definitions import * 
import app.tools.admin_tools # Register Admin Tools 

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
        # CRITICAL FIX: Tools must be declared here or at generation time correctly.
        # Ideally, we inject them dynamically, but for 'start_chat', we should be careful.
        # We will bind tools dynamically in process_message.
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=self.generation_config,
            safety_settings=self.safety_settings
        )

    async def _get_system_prompt(self, role: str, phone: str) -> str:
        """Dynamic Persona Injection based on sender role and DB config."""
        
        # 1. Fetch Knowledge for RAG (Retrieval-Augmented Generation)
        knowledge = await asyncio.to_thread(get_knowledge_base)
        knowledge_str = "\n".join([f"- {k['category'].upper()}: {k['content']}" for k in knowledge])

        # 2. Fetch Prompt from DB (Unified Architecture)
        raw_prompt = await asyncio.to_thread(get_agent_prompt, role)
        
        if not raw_prompt:
            logger.warning(f"⚠️ Falling back to Hardcoded Prompt for {role}")
            # Fallback trivial para evitar crash
            return f"Eres NATALIA. Rol: {role}. Sistema de Prompts en DB falló. Actúa profesional. Contexto: {knowledge_str}"

        # 3. Inject Dynamic Context
        # Usamos safe formatting por si faltan keys en el string de la DB
        try:
            # First format pass
            final_prompt = raw_prompt.replace("{knowledge_str}", knowledge_str).replace("{phone}", phone)
            return final_prompt
        except Exception as e:
            logger.error(f"❌ Error formatting prompt: {e}")
            return raw_prompt

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


        # 1. Lead Identification & Persistence
        lead_id, is_new_lead = await asyncio.to_thread(get_or_create_lead, phone, meta_data)
        await asyncio.to_thread(log_interaction, lead_id, "user", text)

        # 2. Context Retrieval (Memory)
        history_rows = await asyncio.to_thread(get_chat_history, phone, limit=15)

        # 3. Determine Role & Instantiate Agent
        # POLYMORPHIC ARCHITECTURE (Protocol Phase 3)
        from app.agents.router import RoleRouter
        
        context = {
            "db_lead_id": lead_id,
            "is_new_lead": is_new_lead,
            "history": history_rows
        }
        
        agent = RoleRouter.get_agent(phone, context)
        logger.info(f"🧠 Agent Logic Start | Strategy: {agent.role_name} | Phone: {clean_phone}")

        # 2. Tools Retrieval (Restricted by Role)
        # We need to map agent.get_allowed_tools() to actual tool definitions for Gemini
        allowed_tool_names = agent.get_allowed_tools()
        tools_for_gemini = registry.get_tools_by_names(allowed_tool_names)
        logger.info(f"🛠️ Tools enabled: {allowed_tool_names}")

        # 3. Execution (The Agent knows how to think)
        # We need to implement the 'process' method in the agents to handle the LLM loop.
        # But wait, the BaseAgent.process was empty. 
        # To avoid breaking logic, we will keep the LLM interaction HERE for now, 
        # but inject the Agent's Prompt and Tools.
        # Ideally, 'agent.process()' should hold the loop. 
        # For this refactor step, we will use the Agent to CONFIG the session.
        
        final_reply = ""
        try:
            # A. Dynamic System Prompt
            system_instruction = agent.get_system_prompt()
            self.model._system_instruction = system_instruction

            # B. History Preparation
            gemini_history = []
            for msg in history_rows:
                g_role = "user" if msg['role'] == 'user' else "model"
                gemini_history.append({"role": g_role, "parts": [msg['content'] or "..."]})

            # C. Chat Session with Specific Tools
            model_with_tools = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings,
                tools=tools_for_gemini 
            )
            chat_session = model_with_tools.start_chat(history=gemini_history)

            # D. Send Message
            response = await chat_session.send_message_async(text)
            
            # E. Tool Loop (Standardized)
            MAX_TURNS = 3
            for turn in range(MAX_TURNS):
                part = response.candidates[0].content.parts[0]
                if part.function_call:
                    func_call = part.function_call
                    tool_name = func_call.name
                    tool_args = dict(func_call.args)
                    
                    # Security Check: Is this tool allowed for this agent?
                    if tool_name not in allowed_tool_names:
                        logger.warning(f"🚨 SECURITY BLOCKED: {agent.role_name} tried to use {tool_name}")
                        tool_result = "Error: Permission Denied."
                    else:
                        logger.info(f"🛠️ [TOOL EXEC] {tool_name} | Args: {tool_args}")
                        tool_result = registry.execute(tool_name, tool_args)
                    
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
                    final_reply = response.text
                    break
            
            if not final_reply:
                final_reply = response.text

        except Exception as e:
            from app.utils.error_handler import CognitiveShield
            final_reply = await CognitiveShield.handle_error(e, clean_phone, agent.role_name)

        # 4. Log Output
        await asyncio.to_thread(log_interaction, lead_id, "assistant", final_reply)

        return {
            "lead_id": lead_id,
            "reply": final_reply,
            "action": "send_whatsapp",
            "is_new_lead": is_new_lead,
            "metadata": {"agent": agent.role_name}
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
