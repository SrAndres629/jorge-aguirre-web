# =================================================================
# TRACKING.PY - Meta Conversions API (CAPI)
# Jorge Aguirre Flores Web
# =================================================================
import hashlib
import time
import requests
from typing import Optional, Dict, Any
import logging

from app.config import settings

logger = logging.getLogger(__name__)


# =================================================================
# HASHING FUNCTIONS (Requerido por Meta)
# =================================================================

def hash_data(value: str) -> Optional[str]:
    """Hash SHA256 para datos de usuario (requerido por Meta)"""
    if not value:
        return None
    return hashlib.sha256(value.lower().strip().encode('utf-8')).hexdigest()


def generate_external_id(ip: str, user_agent: str) -> str:
    """Genera un ID externo único basado en IP + User Agent"""
    combined = f"{ip}_{user_agent}"
    return hashlib.sha256(combined.encode('utf-8')).hexdigest()[:32]


def generate_fbc(fbclid: str) -> Optional[str]:
    """Genera el parámetro fbc para Meta (click identifier)"""
    if not fbclid:
        return None
    timestamp = int(time.time())
    return f"fb.1.{timestamp}.{fbclid}"


def extract_fbclid_from_fbc(fbc_cookie: str) -> Optional[str]:
    """Extrae el fbclid de una cookie _fbc"""
    if not fbc_cookie or not fbc_cookie.startswith("fb.1."):
        return None
    
    parts = fbc_cookie.split(".")
    if len(parts) >= 4:
        return parts[3]
    return None


# =================================================================
# META CONVERSIONS API
# =================================================================

def send_event(
    event_name: str,
    event_source_url: str,
    client_ip: str,
    user_agent: str,
    event_id: str,
    fbclid: Optional[str] = None,
    external_id: Optional[str] = None,
    custom_data: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Envía un evento a Meta Conversions API
    
    Args:
        event_name: PageView, Lead, ViewContent, Purchase, etc.
        event_source_url: URL de origen del evento
        client_ip: IP del cliente
        user_agent: User Agent del navegador
        event_id: ID único para deduplicación con Pixel
        fbclid: Facebook Click ID (opcional)
        external_id: ID externo del usuario (opcional)
        custom_data: Datos personalizados del evento (opcional)
    
    Returns:
        bool: True si el evento se envió correctamente
    """
    # Construir user_data
    user_data = {
        "client_ip_address": client_ip,
        "client_user_agent": user_agent,
    }
    
    if external_id:
        user_data["external_id"] = hash_data(external_id)
    
    if fbclid:
        user_data["fbc"] = generate_fbc(fbclid)
    
    # Construir evento
    event_data = {
        "event_name": event_name,
        "event_time": int(time.time()),
        "event_id": event_id,
        "action_source": "website",
        "event_source_url": event_source_url,
        "user_data": user_data
    }
    
    if custom_data:
        event_data["custom_data"] = custom_data
    
    # Payload final
    payload = {
        "data": [event_data],
        "access_token": settings.META_ACCESS_TOKEN
    }
    
    # Test event code para desarrollo
    if settings.TEST_EVENT_CODE:
        payload["test_event_code"] = settings.TEST_EVENT_CODE
    
    # Enviar a Meta
    try:
        response = requests.post(
            settings.meta_api_url,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info(f"[META CAPI] ✅ {event_name} enviado | event_id={event_id[:16]}...")
            return True
        else:
            logger.warning(f"[META CAPI] ⚠️ {event_name} | Status: {response.status_code} | {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        logger.error(f"[META CAPI] ⏱️ Timeout enviando {event_name}")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"[META CAPI] ❌ Error enviando {event_name}: {e}")
        return False


def send_n8n_webhook(event_data: Dict[str, Any]) -> bool:
    """Envía el evento a n8n para orquestación"""
    if not settings.N8N_WEBHOOK_URL:
        return False
        
    try:
        response = requests.post(
            settings.N8N_WEBHOOK_URL,
            json=event_data,
            timeout=5
        )
        if response.status_code == 200:
            logger.info(f"✅ Webhook enviado a n8n ({event_data.get('event_name')})")
            return True
    except Exception as e:
        logger.warning(f"⚠️ Error enviando webhook a n8n: {e}")
    return False


# =================================================================
# EVENT SHORTCUTS
# =================================================================

def track_pageview(
    url: str,
    client_ip: str,
    user_agent: str,
    event_id: str,
    fbclid: Optional[str] = None,
    external_id: Optional[str] = None
) -> bool:
    """Shortcut para enviar PageView"""
    return send_event(
        event_name="PageView",
        event_source_url=url,
        client_ip=client_ip,
        user_agent=user_agent,
        event_id=event_id,
        fbclid=fbclid,
        external_id=external_id
    )


def track_lead(
    url: str,
    client_ip: str,
    user_agent: str,
    event_id: str,
    source: str,
    fbclid: Optional[str] = None,
    external_id: Optional[str] = None,
    service_data: Optional[Dict[str, Any]] = None
) -> bool:
    """Shortcut para enviar Lead"""
    custom_data = {
        "content_name": source,
        "content_category": "lead",
        "lead_source": source
    }
    
    # Merge granular data if available
    if service_data:
        custom_data.update({
            "content_name": service_data.get("name", source),
            "content_ids": [service_data.get("id")] if service_data.get("id") else [],
            "content_category": service_data.get("intent", "lead"),
            "trigger_location": source
        })
    
    return send_event(
        event_name="Lead",
        event_source_url=url,
        client_ip=client_ip,
        user_agent=user_agent,
        event_id=event_id,
        fbclid=fbclid,
        external_id=external_id,
        custom_data=custom_data
    )


def track_viewcontent(
    url: str,
    client_ip: str,
    user_agent: str,
    event_id: str,
    service: str,
    category: str,
    price: float = 0,
    fbclid: Optional[str] = None,
    external_id: Optional[str] = None
) -> bool:
    """Shortcut para enviar ViewContent"""
    custom_data = {
        "content_name": service,
        "content_category": category,
        "content_type": "service",
        "value": price,
        "currency": "USD"
    }
    
    return send_event(
        event_name="ViewContent",
        event_source_url=url,
        client_ip=client_ip,
        user_agent=user_agent,
        event_id=event_id,
        fbclid=fbclid,
        external_id=external_id,
        custom_data=custom_data
    )


def track_slider_interaction(
    url: str,
    client_ip: str,
    user_agent: str,
    event_id: str,
    service_name: str,
    service_id: str,
    interaction_type: str,
    fbclid: Optional[str] = None,
    external_id: Optional[str] = None
) -> bool:
    """Shortcut para enviar SliderInteraction (Custom Event)"""
    custom_data = {
        "content_name": service_name,
        "content_id": service_id,
        "interaction_type": interaction_type,
        "content_category": "interaction"
    }
    
    return send_event(
        event_name="SliderInteraction",
        event_source_url=url,
        client_ip=client_ip,
        user_agent=user_agent,
        event_id=event_id,
        fbclid=fbclid,
        external_id=external_id,
        custom_data=custom_data
    )


def track_purchase(
    external_id: str,
    fbclid: Optional[str],
    value: float = 350.00,
    currency: str = "USD"
) -> bool:
    """Shortcut para enviar Purchase (desde Admin)"""
    event_id = f"purchase_{int(time.time() * 1000)}"
    
    custom_data = {
        "value": value,
        "currency": currency,
        "content_name": "Servicio de Maquillaje Permanente",
        "content_category": "beauty_service",
        "content_type": "service"
    }
    
    return send_event(
        event_name="Purchase",
        event_source_url="https://jorgeaguirreflores.com/admin",
        client_ip="127.0.0.1",
        user_agent="Admin Dashboard",
        event_id=event_id,
        fbclid=fbclid,
        external_id=external_id,
        custom_data=custom_data
    )
