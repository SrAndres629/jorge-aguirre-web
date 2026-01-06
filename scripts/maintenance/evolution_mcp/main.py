
from mcp.server.fastmcp import FastMCP
import asyncio
# Import tools logic
from tools import messaging, instances, social, webhooks

# Initialize Server
mcp = FastMCP("Evolution API Manager 3.0 (Full Suite)")

# =================================================================
# MESSAGING TOOLS
# =================================================================

@mcp.tool()
async def send_whatsapp_message(number: str, text: str, instance: str = "JorgeMain") -> str:
    """Send text message."""
    result = await messaging.send_text(number, text, instance)
    if result.get("error"): return f"❌ Error: {result['message']}"
    return f"✅ Message sent"

@mcp.tool()
async def send_media_message(number: str, media_type: str, url: str, caption: str = "", instance: str = "JorgeMain") -> str:
    """Send media (image, video, audio, document)."""
    result = await messaging.send_media(number, media_type, url, caption, instance)
    if result.get("error"): return f"❌ Error: {result['message']}"
    return f"✅ Media sent"

# =================================================================
# INSTANCE TOOLS
# =================================================================

@mcp.tool()
async def check_instance_status(instance: str = "JorgeMain") -> str:
    """Check connection status."""
    res = await instances.get_status(instance)
    return str(res)

@mcp.tool()
async def list_all_instances() -> str:
    """List all instances."""
    res = await instances.list_instances()
    return str(res)

@mcp.tool()
async def restart_instance(instance: str = "JorgeMain") -> str:
    """Restart an instance."""
    res = await instances.restart_instance(instance)
    return str(res)

@mcp.tool()
async def create_instance(name: str, token: str = None) -> str:
    """Create a new instance."""
    res = await instances.create_instance(name, token)
    return str(res)

@mcp.tool()
async def delete_instance(instance: str, force: bool = False) -> str:
    """Delete an instance (Careful!)."""
    res = await instances.delete_instance(instance)
    return str(res)

# =================================================================
# SOCIAL SEARCH & MANAGEMENT
# =================================================================

@mcp.tool()
async def check_whatsapp_number(number: str, instance: str = "JorgeMain") -> str:
    """Verify if a number is registered on WhatsApp."""
    res = await social.check_number(number, instance)
    return str(res)

@mcp.tool()
async def block_user(number: str, instance: str = "JorgeMain") -> str:
    """Block a contact."""
    res = await social.block_contact(number, instance, block=True)
    return str(res)

@mcp.tool()
async def get_profile_picture(number: str, instance: str = "JorgeMain") -> str:
    """Get profile picture URL."""
    res = await social.get_profile_pic(number, instance)
    return str(res)

# =================================================================
# WEBHOOKS
# =================================================================

@mcp.tool()
async def configure_webhook(url: str, instance: str = "JorgeMain") -> str:
    """Connect instance to n8n."""
    events = ["MESSAGES_UPSERT", "MESSAGES_UPDATE", "SEND_MESSAGE", "CONNECTION_UPDATE"]
    res = await webhooks.set_webhook(url, True, events, instance)
    return str(res)

if __name__ == "__main__":
    mcp.run()
