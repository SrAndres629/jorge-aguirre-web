
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger("GatewayParams")

class StandardMessage:
    def __init__(self, phone: str, text: str, name: str, source: str, raw_data: Dict[str, Any]):
        self.phone = phone
        self.text = text
        self.name = name
        self.source = source
        self.timestamp = raw_data.get("messageTimestamp")
        self.id = raw_data.get("key", {}).get("id")

def normalize_evolution_payload(body: Dict[str, Any]) -> Optional[StandardMessage]:
    """
    Transforms Evolution API v2 payload into a Canonical StandardMessage.
    Implements f: W -> G (Injective)
    """
    try:
        # 1. Validation (Is it an Upsert?)
        if body.get("type") != "MESSAGES_UPSERT":
            return None
            
        data = body.get("data", {})
        key = data.get("key", {})
        
        # 2. Filter: Ignore Echoes (From Me)
        if key.get("fromMe", False):
            return None

        # 3. Extraction: Phone
        remote_jid = key.get("remoteJid", "")
        phone = remote_jid.split("@")[0] if "@" in remote_jid else remote_jid
        
        # 4. Extraction: Text (Polymorphic Content)
        message_content = data.get("message", {})
        text = (
            message_content.get("conversation") or 
            message_content.get("extendedTextMessage", {}).get("text") or
            message_content.get("imageMessage", {}).get("caption") or
            ""
        )
        
        if not text:
            logger.warning(f"⚠️ [GATEWAY] Empty/Unsupported Content from {phone}")
            return None

        # 5. Extraction: Name
        push_name = data.get("pushName", "Unknown")

        # 6. Canonical Object
        return StandardMessage(
            phone=phone,
            text=text,
            name=push_name,
            source="evolution_v2",
            raw_data=data
        )

    except Exception as e:
        logger.error(f"❌ [GATEWAY] Normalization Failed: {e}")
        return None
