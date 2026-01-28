
import logging
import traceback
from app.evolution import evolution_service
from app.roles import Role

logger = logging.getLogger("CognitiveShield")

# Error Constants
ERR_CRITICAL_BRAIN = "CRITICAL_BRAIN"   # AI/LLM Failure
ERR_MEMORY_LOSS = "MEMORY_LOSS"       # DB Failure
ERR_SPEECH_JAM = "SPEECH_JAM"         # Evolution API/Network
ERR_LOGIC_LOOP = "LOGIC_LOOP"         # Code/Bug

# Admin Phone (Hardcoded for safety in error handler)
ADMIN_PHONE = "59178113055" 

class CognitiveShield:
    """
    Self-Diagnosing Error Handler.
    Maps technical exceptions to:
    1. Polite excuses for Clients.
    2. Debug reports for Admins.
    """
    
    @staticmethod
    async def handle_error(e: Exception, phone: str, role: str) -> str:
        """
        Main entry point for error handling.
        Returns the reply string to be sent to the user.
        Background: Sends alert to Admin.
        """
        # 1. Diagnose Error
        error_code, debug_info = CognitiveShield._diagnose(e)
        
        logger.error(f"🛡️ SHIELD ACTIVATED | Code: {error_code} | User: {phone} | Error: {debug_info}")

        # 2. Alert Admin (Fire and Forget in background if possible, 
        # but here we await it to ensure delivery before return)
        # Only alert if user is NOT admin (to avoid loop) and error is notable
        if phone != ADMIN_PHONE:
            await CognitiveShield._alert_admin(phone, error_code, debug_info)

        # 3. Formulate Response based on Role
        if role in [Role.GOD.value, Role.SUPERVISOR.value]:
            # Technical Detailed Response for Admin/Staff
            return (
                f"⚠️ **SYSTEM ALERT**\n\n"
                f"**Code:** `{error_code}`\n"
                f"**Error:** {str(e)}\n"
                f"**Trace:** `{traceback.format_exc()[-100:]}`\n\n"
                f"*Check Render Logs.*"
            )
        else:
            # Polite Excuse for Clients
            return CognitiveShield._get_polite_excuse(error_code)

    @staticmethod
    def _diagnose(e: Exception) -> tuple[str, str]:
        """Classify exception into domain categories"""
        e_str = str(e).lower()
        e_type = type(e).__name__
        
        if "google" in e_str or "generativeai" in e_str or "quota" in e_str:
            return ERR_CRITICAL_BRAIN, f"Gemini Error: {e_type}"
            
        if "postgres" in e_str or "connection" in e_str or "cursor" in e_str or "operationalerror" in e_str.lower():
            return ERR_MEMORY_LOSS, f"Database Error: {e_type}"
            
        if "evolution" in e_str or "timeout" in e_str or "502" in e_str:
            return ERR_SPEECH_JAM, f"Evolution API Error: {e_type}"
            
        return ERR_LOGIC_LOOP, f"Internal Logic Error: {e_type} - {e_str}"

    @staticmethod
    def _get_polite_excuse(code: str) -> str:
        """Map error code to brand-safe copy"""
        excuses = {
            ERR_CRITICAL_BRAIN: "Disculpa, estoy analizando tu caso con mucha profundidad y mis neuronas pidieron un segundo. 🧠 ¿Me repites lo último?",
            ERR_MEMORY_LOSS: "Estoy sincronizando mi agenda en tiempo real y la señal está oscilando. Dame un minuto. 🗓️",
            ERR_SPEECH_JAM: "La conexión de WhatsApp está un poco lenta. ¿Podrías repetirme eso? 📶",
            ERR_LOGIC_LOOP: "Estoy actualizando mis listas de precios y servicios. Un momento por favor. 💎"
        }
        return excuses.get(code, "Disculpa, tuve un pequeño lapso. ¿En qué estábamos? ✨")

    @staticmethod
    async def _alert_admin(user_phone: str, code: str, debug_info: str):
        """Send silent alarm to Admin"""
        try:
            msg = (
                f"👮♂️ **SECURITY WATCHDOG**\n"
                f"User `{user_phone}` encountered error: `{code}`.\n"
                f"Debug: `{debug_info}`"
            )
            # Use evolution service directly
            await evolution_service.send_text(ADMIN_PHONE, msg)
        except Exception as crash:
            logger.critical(f"❌ Failed to alert admin: {crash}")
