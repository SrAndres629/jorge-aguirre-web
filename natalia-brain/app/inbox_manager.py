import asyncio
import logging
from typing import Dict, Optional, List
import time
from app.natalia import natalia
from app.evolution import evolution_service
from app.database import log_interaction

logger = logging.getLogger("InboxManager")

class InboxManager:
    """
    Gestor de Bandeja de Entrada Cognitiva.
    Agrupa mensajes consecutivos (Deboucing) y aplica Delay Dinámico.
    """
    def __init__(self):
        # Buffer: { phone: { "messages": [txt1, txt2], "task": asyncio.Task, "meta": {} } }
        self.buffers: Dict[str, Dict] = {}
        self.active_processing_count = 0  # Para la carga dinámica

        # Configuración
        self.DEBOUNCE_SECONDS = 15.0  # Tiempo de espera para agrupar mensajes
        self.BASE_DELAY_SECONDS = 12.0 # Delay inicial antes de responder
        self.LOAD_FACTOR_SECONDS = 0.6 # Aumento por cada tarea activa

    async def add_message(self, phone: str, text: str, meta_data: Optional[dict] = None):
        """
        Agrega un mensaje al buffer del usuario. Reinicia el temporizador de Debounce.
        """
        if phone not in self.buffers:
            self.buffers[phone] = {
                "messages": [],
                "task": None,
                "meta": meta_data or {},
                "last_activity": time.time()
            }
        
        # 1. Agregar mensaje a la pila
        self.buffers[phone]["messages"].append(text)
        self.buffers[phone]["last_activity"] = time.time()
        
        # Actualizar metadata si llega nueva info (ejs: nombre)
        if meta_data:
            self.buffers[phone]["meta"].update(meta_data)
        
        logger.info(f"📥 [BUFFER] {phone}: Mensaje agregado. Total en cola: {len(self.buffers[phone]['messages'])}")

        # 2. Reiniciar el temporizador (Debounce)
        if self.buffers[phone]["task"] and not self.buffers[phone]["task"].done():
            self.buffers[phone]["task"].cancel()
            logger.debug(f"⏳ [DEBOUNCE] {phone}: Timer reiniciado.")

        # 3. Crear nueva tarea de espera
        self.buffers[phone]["task"] = asyncio.create_task(self._process_buffer_task(phone))

    async def _process_buffer_task(self, phone: str):
        """
        Tarea asíncrona que espera a que el usuario deje de escribir y luego ejecuta el procesamiento.
        """
        try:
            # A. Fase de Silencio (Esperar a que termine de enviar mensajes)
            await asyncio.sleep(self.DEBOUNCE_SECONDS)
            
            # B. Fase de Procesamiento
            self.active_processing_count += 1
            buffer_data = self.buffers.pop(phone, None)
            
            if not buffer_data or not buffer_data["messages"]:
                return

            full_text = "\n".join(buffer_data["messages"])
            meta = buffer_data["meta"]
            
            logger.info(f"🧠 [THINKING] {phone}: Procesando bloque de {len(buffer_data['messages'])} mensajes.")
            
            # C. Dynamic Artificial Delay (Humanización + Rate Limit)
            # Delay base + (Carga del sistema * Factor)
            extra_delay = self.active_processing_count * self.LOAD_FACTOR_SECONDS
            total_delay = self.BASE_DELAY_SECONDS + extra_delay
            
            logger.info(f"🕒 [DELAY] {phone}: Esperando {total_delay:.2f}s (Carga: {self.active_processing_count})")
            await asyncio.sleep(total_delay)

            # D. Ejecución Neuronal
            result = await natalia.process_message(phone, full_text, meta)
            
            # E. Respuesta
            if result.get("action") == "send_whatsapp":
                await evolution_service.send_text(phone, result["reply"])

        except asyncio.CancelledError:
            # Tarea cancelada porque llegó otro mensaje (Debounce normal)
            pass
        except Exception as e:
            logger.error(f"❌ Error en InboxManager para {phone}: {e}")
            # Fallback de emergencia
            await evolution_service.send_text(phone, "Disculpa, tuve un lapso neuronal. ¿Podrías repetirme eso?")
        finally:
            if not asyncio.current_task().cancelled():
                self.active_processing_count = max(0, self.active_processing_count - 1)

# Singleton Export
inbox_manager = InboxManager()
