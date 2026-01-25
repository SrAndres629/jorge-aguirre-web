# =================================================================
# CELERY TASKS
# Jorge Aguirre Flores Web
# =================================================================
from app.celery_app import celery_app
from app.tracking import send_event, send_n8n_webhook
from app.database import save_visitor, upsert_contact_advanced, save_message
import logging

logger = logging.getLogger("worker")

# =================================================================
# DATABASE TASKS
# =================================================================

@celery_app.task(bind=True, name="save_visitor_task", default_retry_delay=5, max_retries=3)
def save_visitor_task(self, external_id, fbclid, client_ip, user_agent, source, utm_data):
    """Persist visitor data to DB asynchronously"""
    try:
        save_visitor(
            external_id=external_id,
            fbclid=fbclid,
            ip_address=client_ip,
            user_agent=user_agent,
            source=source,
            utm_data=utm_data
        )
        logger.info(f"✅ Visitor saved: {external_id}")
    except Exception as e:
        logger.error(f"❌ Error saving visitor: {e}")
        raise self.retry(exc=e)

@celery_app.task(bind=True, name="upsert_contact_task", default_retry_delay=10, max_retries=5)
def upsert_contact_task(self, contact_payload):
    """Persist lead/contact data to DB asynchronously (Natalia Sync)"""
    try:
        upsert_contact_advanced(contact_payload)
        logger.info(f"✅ Natalia Sync: {contact_payload.get('phone')}")
    except Exception as e:
        logger.error(f"❌ Error syncing Natalia contact: {e}")
        raise self.retry(exc=e)

@celery_app.task(bind=True, name="save_message_task", default_retry_delay=5, max_retries=3)
def save_message_task(self, phone, role, content):
    """Save message to contact history for AI context and trigger Lead Conversion"""
    from app.database import (
        save_message, check_if_lead_sent, get_meta_data_by_ref, 
        mark_lead_sent, get_cursor
    )
    import re

    try:
        # 1. Persistencia del mensaje
        save_message(phone, role, content)
        
        # 2. 🛡️ TRUE LEAD Protocol: Solo procesamos si el mensaje es del USUARIO (role='user')
        if role != "user":
            return True

        # 3. 🛡️ Verificación de Escudo Financiero (Deduplicación)
        if check_if_lead_sent(phone):
            logger.info(f"🛡️ [CAPI SHIELD] Lead already sent for {phone}. Skipping.")
            return True

        # 🛡️ Pillar 3: Natalia's Smart Filter
        # Solo enviamos el Lead a Meta si el usuario ha enviado al menos 2 mensajes (Interés certificado)
        from app.database import get_user_message_count
        msg_count = get_user_message_count(phone)
        if msg_count < 2:
            logger.info(f"⏳ [SMART FILTER] Message count for {phone} is {msg_count}. Waiting for more interaction to fire Lead.")
            return True

        # 4. Enriquecimiento de Datos via [Ref Tag] y Natalia's Brain
        from app.natalia import natalia
        # Volvemos a procesar ligeramente para obtener metadatos de valor (VBO)
        brain_result = natalia.process_message(phone, content) 
        meta_vbo = brain_result.get("metadata", {})
        
        # 🛑 Pillar 4: Anti-Junk Signal (Negative Feedback)
        if meta_vbo.get("is_junk"):
            logger.info(f"🛑 [ANTI-JUNK] Sending Negative Signal for {phone}")
            from app.tasks import send_meta_event_task
            send_meta_event_task.delay(
                event_name="Other", # Evento genérico para no inflar leads
                event_source_url="https://jorgeaguirreflores.com/whatsapp_spam",
                client_ip="127.0.0.1",
                user_agent="Natalia Anti-Junk",
                event_id=f"junk_{phone}",
                phone=phone,
                custom_data={"disqualified_reason": "negative_intent", "is_junk": True}
            )
            mark_lead_sent(phone) # Bloqueamos cualquier cobro futuro de este número
            return True
        meta_data = None
        if ref_match:
            ref_tag = ref_match.group(1)
            meta_data = get_meta_data_by_ref(ref_tag)
            if meta_data:
                logger.info(f"🧬 [DATA ENRICHMENT] Found meta data for ref {ref_tag}")

        # 5. Disparo de Conversión 'Lead' (Backend Authority + VBO)
        from app.tasks import send_meta_event_task
        
        event_id = f"lead_be_v2_{phone}"
        send_meta_event_task.delay(
            event_name="Lead",
            event_source_url="https://jorgeaguirreflores.com/whatsapp_conversion",
            client_ip=meta_data.get('ip_address', '127.0.0.1') if meta_data else '127.0.0.1',
            user_agent=meta_data.get('user_agent', 'Evolution API') if meta_data else 'Evolution API',
            event_id=event_id,
            fbclid=meta_data.get('fbclid') if meta_data else None,
            fbp=None,
            external_id=None,
            phone=phone,
            custom_data={
                "lead_source": "whatsapp_qualified",
                "content_category": meta_vbo.get("intent", "general"),
                "value": meta_vbo.get("value", 50.0), # 💰 VBO Pillar 1
                "currency": meta_vbo.get("currency", "USD"),
                "phone": phone
            }
        )
        
        logger.info(f"🚀 [TRUE LEAD v2.0] Qualified conversion sent for {phone} - Value: {meta_vbo.get('value')}")
        return True

    except Exception as e:
        logger.error(f"❌ Error saving message/triggering lead: {e}")
        raise self.retry(exc=e)

# =================================================================
# EXTERNAL API TASKS
# =================================================================

@celery_app.task(bind=True, name="send_meta_event_task", default_retry_delay=5, max_retries=3)
def send_meta_event_task(self, event_name, event_source_url, client_ip, user_agent, event_id, fbclid, fbp, external_id, custom_data):
    """Send event to Facebook Conversions API with Executive Deduplication Shield"""
    from app.database import check_if_lead_sent, mark_lead_sent
    
    # 🛡️ Executive Shield: Bloqueo de duplicados para optimizar presupuesto
    phone = None
    if event_name == "Lead":
        phone = custom_data.get('phone') if custom_data else None
        if phone and check_if_lead_sent(phone):
            logger.info(f"🛡️ [ABORT MISSION] Lead already paid for {phone}. Skipping CAPI call to save budget.")
            return True

    try:
        success = send_event(
            event_name=event_name,
            event_source_url=event_source_url,
            client_ip=client_ip,
            user_agent=user_agent,
            event_id=event_id,
            fbclid=fbclid,
            fbp=fbp,
            external_id=external_id,
            custom_data=custom_data
        )
        if not success:
            raise Exception("Meta API returned failure")
            
        # 🛡️ Registro de conversión exitosa
        if event_name == "Lead" and phone:
            mark_lead_sent(phone)
            
        logger.info(f"✅ Meta Event sent: {event_name}")
    except Exception as e:
        logger.warning(f"⚠️ Meta send failed (retrying): {e}")
        raise self.retry(exc=e)

@celery_app.task(bind=True, name="send_n8n_webhook_task", default_retry_delay=5, max_retries=5)
def send_n8n_webhook_task(self, payload):
    """Send webhook to n8n"""
    try:
        success = send_n8n_webhook(payload)
        if not success:
            raise Exception("n8n Webhook failed")
        logger.info("✅ n8n Webhook sent")
    except Exception as e:
        logger.warning(f"⚠️ n8n send failed (retrying): {e}")
        raise self.retry(exc=e)

@celery_app.task(bind=True, name="track_booking_confirmed_task", default_retry_delay=5, max_retries=3)
def track_booking_confirmed_task(self, phone, service_name, value):
    """Pillar 2: The Gold Feedback Loop - Sends 'Schedule' or 'Purchase' to Meta when booking is confirmed"""
    from app.database import get_meta_data_by_ref
    from app.tracking import send_event
    
    # Intentamos recuperar cookies por historial (sin Ref Tag directo aquí, usamos el teléfono)
    # En una implementación real más compleja, buscaríamos el último visitor_id vinculado al contacto
    try:
        success = send_event(
            event_name="Schedule", # O 'Purchase' según prefiera el cliente
            event_source_url="https://jorgeaguirreflores.com/admin/booking",
            client_ip="127.0.0.1",
            user_agent="Server Offline Trigger",
            event_id=f"sched_{phone}_{int(time.time())}",
            phone=phone,
            custom_data={
                "content_name": service_name,
                "value": value,
                "currency": "USD",
                "status": "confirmed_offline"
            }
        )
        if success:
            logger.info(f"🏆 [GOLD LOOP] Appointment tracked for {phone}")
        return success
    except Exception as e:
        logger.error(f"❌ Gold Loop Error: {e}")
        raise self.retry(exc=e)
@celery_app.task(bind=True, name="ghost_rescue_task", default_retry_delay=300, max_retries=2)
def ghost_rescue_task(self, phone):
    """
    CONVERSION STRATEGIST: Ghost Protocol
    Triggers a soft diagnostic follow-up if a lead hasn't responded in 24h.
    """
    from app.database import get_chat_history
    from app.evolution import evolution_service
    
    history = get_chat_history(phone, limit=1)
    if not history or history[0]['role'] == 'user':
        return # They responded, no rescue needed
        
    # Soft Diagnostic Hook (Expert Frame)
    rescue_text = (
        "Hola, soy Natalia de nuevo. Estaba revisando tu caso con Jorge y nos quedó una duda: "
        "¿buscas corregir un diseño previo o es para un rostro virgen?\n\n"
        "Pregunto porque la técnica que usaríamos cambia completamente según tu respuesta. ✨"
    )
    
    try:
        evolution_service.send_text(phone, rescue_text)
        logger.info(f"👻 [GHOST PROTOCOL] Rescue signal sent to {phone}")
    except Exception as e:
        logger.error(f"❌ Ghost Rescue failed: {e}")
        raise self.retry(exc=e)
