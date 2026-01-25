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

        # 4. Enriquecimiento de Datos via [Ref Tag]
        ref_match = re.search(r"\[Ref: ([a-zA-Z0-9]+)\]", content)
        meta_data = None
        if ref_match:
            ref_tag = ref_match.group(1)
            meta_data = get_meta_data_by_ref(ref_tag)
            if meta_data:
                logger.info(f"🧬 [DATA ENRICHMENT] Found meta data for ref {ref_tag}")

        # 5. Disparo de Conversión 'Lead' (Backend Authority)
        # Extraemos cookies si se encontraron, si no, disparamos solo con el teléfono (6/10 vs 10/10)
        from app.tasks import send_meta_event_task
        
        event_id = f"lead_be_{phone}_{int(time.time())}"
        send_meta_event_task.delay(
            event_name="Lead",
            event_source_url="https://jorgeaguirreflores.com/whatsapp_conversion",
            client_ip=meta_data.get('ip_address', '127.0.0.1') if meta_data else '127.0.0.1',
            user_agent=meta_data.get('user_agent', 'Evolution API') if meta_data else 'Evolution API',
            event_id=event_id,
            fbclid=meta_data.get('fbclid') if meta_data else None,
            fbp=None, # Implementación de recuperación de fbp pendiente si no está en visitor
            external_id=None,
            phone=phone, # 🚀 PRIMARY KEY PARA MATCHING
            custom_data={
                "lead_source": "whatsapp_confirmed",
                "content_category": "confirmed_lead",
                "phone": phone
            }
        )
        
        logger.info(f"🚀 [TRUE LEAD] Backend conversion triggered for {phone}")
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
