
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger("GatewayParams")

class UserMessage:
    """
    Standardized Message Object for the Neural Core.
    Protocol: { sender, text, type, timestamp }
    """
    def __init__(self, sender: str, text: str, message_type: str, timestamp: int, name: str = "Unknown", source: str = "evolution_v2", id: str = None, raw_data: Dict = None):
        self.sender = sender
        self.text = text
        self.type = message_type
        self.timestamp = timestamp
        self.name = name
        self.source = source
        self.id = id
        # Alias for backward compatibility with existing codebase
        self.phone = sender 

def normalize_evolution_payload(body: Dict[str, Any]) -> Optional[UserMessage]:
    """
    Transforms Evolution API v2 payload into a Clean UserMessage.
    Implements f: W -> G (Injective)
    Handles: text, extendedText, audio
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

        # 3. Extraction: Sender (Phone)
        remote_jid = key.get("remoteJid", "")
        sender = remote_jid.split("@")[0] if "@" in remote_jid else remote_jid
        
        # 4. Extraction: Content Polymorphism
        message_content = data.get("message", {})
        msg_text = ""
        msg_type = "text"

        # Handle Text
        if "conversation" in message_content:
            msg_text = message_content["conversation"]
        elif "extendedTextMessage" in message_content:
            msg_text = message_content["extendedTextMessage"].get("text", "")
        elif "imageMessage" in message_content:
            msg_text = message_content["imageMessage"].get("caption", "[Image]")
            msg_type = "image"
        # Handle Audio (Critical)
        elif "audioMessage" in message_content:
            msg_text = "[Audio Message]"
            msg_type = "audio"
            # In a real scenario, we would extract the media URL/Base64 here
        
        if not msg_text and msg_type == "text":
            logger.warning(f"⚠️ [GATEWAY] Empty/Unsupported Content from {sender}")
            return None

        # 5. Extraction: Metadata
        push_name = data.get("pushName", "Unknown")
        timestamp = data.get("messageTimestamp")

        # 6. Canonical Object
        return UserMessage(
            sender=sender,
            text=msg_text,
            message_type=msg_type,
            timestamp=timestamp,
            name=push_name,
            source="evolution_v2",
            id=key.get("id"),
            raw_data=data
        )

    except Exception as e:
        logger.error(f"❌ [GATEWAY] Normalization Failed: {e}")
        return None
