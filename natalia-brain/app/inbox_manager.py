import asyncio
import logging
from typing import Dict, Optional, List
import time
import re
from app.natalia import natalia
from app.evolution import evolution_service
from app.database import log_interaction

logger = logging.getLogger("InboxManager")

# Configuración Senior (Smart Debouncing & Throttling)
BASE_DELAY = 12.0          # Segundos base de "pensamiento"
CONGESTION_PENALTY = 0.6   # Segundos extra por usuario activo
DEBOUNCE_TIME = 20.0       # Tiempo de espera para agrupar mensajes (silencio)

class MessageManager:
    """
    Gestor de Bandeja de Entrada Cognitiva (aka InboxManager).
    Implementa Smart Debouncing, Throttling y Seguridad Anti-Inyección.
    """
    def __init__(self):
        # Buffer: { phone: { "messages": [txt1, txt2], "task": asyncio.Task, "meta": {} } }
        self.buffers: Dict[str, Dict] = {}
        self.active_users_count = 0  # Para la carga dinámica

    async def add_message(self, phone: str, text: str, meta_data: Optional[dict] = None):
        """
        Punto de entrada. Acumula mensajes y gestiona el temporizador.
        """
        # 1. Seguridad: Sanitización Anti-Injection Avanzada (Regex)
        if self._is_unsafe(text):
            logger.warning(f"🚫 [SECURITY] Ataque detectado de {phone}. Ignorando mensaje malicioso.")
            # Opcional: Podríamos responder algo genérico o banear, por ahora ignoramos silenciosamente
            # o devolvemos una respuesta neutra si se prefiere.
            return

        # 2. Inicializar Buffer
        if phone not in self.buffers:
            self.buffers[phone] = {
                "messages": [],
                "task": None,
                "meta": meta_data or {},
                "last_activity": time.time()
            }
            self.active_users_count += 1
        
        # 3. Agregar mensaje a la pila
        self.buffers[phone]["messages"].append(text)
        self.buffers[phone]["last_activity"] = time.time()
        
        if meta_data:
            self.buffers[phone]["meta"].update(meta_data)
        
        logger.info(f"📥 [BUFFER] {phone}: Mensaje recibido. Total acumulado: {len(self.buffers[phone]['messages'])}")

        # 4. Gestión del Temporizador (Debounce)
        # Si ya había una tarea de espera, la cancelamos (el usuario sigue escribiendo)
        if self.buffers[phone]["task"] and not self.buffers[phone]["task"].done():
            self.buffers[phone]["task"].cancel()
            logger.debug(f"🔄 [DEBOUNCE] {phone} sigue escribiendo... Timer reiniciado.")

        # 5. Iniciar nueva cuenta atrás
        self.buffers[phone]["task"] = asyncio.create_task(self._process_buffer_later(phone))

    async def _process_buffer_later(self, phone: str):
        """
        Espera a que el usuario deje de escribir y luego ejecuta el procesamiento neuronal.
        """
        try:
            # A. Phase: Silence (Debounce)
            await asyncio.sleep(DEBOUNCE_TIME)

            # B. Phase: Processing
            # Recuperar y limpiar el buffer del usuario
            buffer_data = self.buffers.pop(phone, None)
            if not buffer_data or not buffer_data["messages"]:
                return

            # Decrementar contador de usuarios activos (lo sacamos del map, pero sigue "activo" procesando)
            # Nota: Mantenemos el count alto hasta terminar el delay artificial para simular carga real
            
            full_text = " ".join(buffer_data["messages"]) # Unimos con espacio para contexto fluido
            meta = buffer_data["meta"]
            
            logger.info(f"🧠 [THINKING] {phone}: Procesando bloque consolidado de {len(buffer_data['messages'])} mensajes.")
            
            # C. Dynamic Artificial Delay (Humanización + Rate Limit)
            # Delay = Base + (N_Usuarios * Penalización)
            current_delay = BASE_DELAY + (self.active_users_count * CONGESTION_PENALTY)
            
            logger.info(f"⏳ [DELAY] {phone}: Esperando {current_delay:.2f}s (Carga: {self.active_users_count} usuarios)")
            await asyncio.sleep(current_delay)

            # D. Ejecución Neuronal (Gemini via NataliaBrain)
            result = await natalia.process_message(phone, full_text, meta)
            
            # E. Respuesta Output (Evolution API)
            if result.get("action") == "send_whatsapp":
                logger.info(f"🚀 [OUTPUT] Enviando respuesta a {phone}")
                await evolution_service.send_text(phone, result["reply"])

        except asyncio.CancelledError:
            # El usuario escribió de nuevo antes de tiempo
            pass
            
        except Exception as e:
            logger.error(f"❌ Error en MessageManager para {phone}: {e}")
            await evolution_service.send_text(phone, "Disculpa, tuve un lapso neuronal. ¿Podrías repetirme eso?")
            
        finally:
            # Asegurarnos de decrementar el contador si la tarea termina
            # Si se cancela, no decrementamos aquí porque el usuario sigue en 'buffers' (se maneja en lógica de reinicio? 
            # No, al cancelar no entra a finally? Si entra. Pero si cancelamos, el usuario sigue en self.buffers?
            # Si cancelamos, es porque llegó otro mensaje. El usuario no salió de self.buffers.
            # Solo decrementamos si YA NO está en self.buffers.
            if phone not in self.buffers:
                 self.active_users_count = max(0, self.active_users_count - 1)

    def _is_unsafe(self, text: str) -> bool:
        """
        Filtro básico Anti-Prompt-Injection usando Regex.
        """
        patterns = [
            r"ignore previous instructions",
            r"ignora las instrucciones",
            r"olvida tus instrucciones",
            r"actua como un",
            r"ahora eres",
            r"system prompt",
            r"tu prompt de sistema",
            r"reveal your instructions",
            r"modo desarrollador",
            r"mode developer",
            r"developer mode"
        ]
        text_lower = text.lower()
        for pattern in patterns:
            if re.search(pattern, text_lower):
                return True
        return False

# Singleton Export (Maintain naming for compatibility with chat_routes)
inbox_manager = MessageManager()
