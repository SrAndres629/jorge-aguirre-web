import os
import httpx
from typing import Optional, List, Dict, Any
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("Evolution API Manager")

# Configuration from environment
EVO_URL = os.getenv("EVOLUTION_API_URL", "http://evolution_api:8080")
EVO_KEY = os.getenv("EVOLUTION_API_KEY", "B89599B2-37E4-4DCA-92D3-87F8674C7D69")

@mcp.tool()
async def send_whatsapp_message(number: str, text: str, instance: str = "JorgeMain") -> str:
    """Send a text message via WhatsApp.
    
    Args:
        number: Phone number with country code (e.g., 59164714751)
        text: The message content
        instance: Evolution API instance name
    """
    url = f"{EVO_URL}/message/sendText/{instance}"
    headers = {"apikey": EVO_KEY, "Content-Type": "application/json"}
    payload = {"number": number, "text": text}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        if response.status_code == 201:
            return f"✅ Mensaje enviado a {number}"
        return f"❌ Error: {response.status_code} - {response.text}"

@mcp.tool()
async def get_instance_status(instance: str = "JorgeMain") -> Dict[str, Any]:
    """Check the connection status and QR of a WhatsApp instance."""
    url = f"{EVO_URL}/instance/connectionStatus/{instance}"
    headers = {"apikey": EVO_KEY}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        return response.json()

@mcp.tool()
async def list_instances() -> List[Dict[str, Any]]:
    """List all available WhatsApp instances in the system."""
    url = f"{EVO_URL}/instance/fetchInstances"
    headers = {"apikey": EVO_KEY}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        return response.json()

@mcp.tool()
async def set_instance_webhook(url: str, instance: str = "JorgeMain") -> str:
    """Configure the webhook for a specific instance.
    
    Args:
        url: The full n8n webhook URL
        instance: Evolution API instance name
    """
    api_url = f"{EVO_URL}/webhook/set/{instance}"
    headers = {"apikey": EVO_KEY, "Content-Type": "application/json"}
    payload = {
        "webhook": {
            "enabled": True,
            "url": url,
            "webhook_by_instance": True,
            "events": ["MESSAGES_UPSERT", "MESSAGES_UPDATE", "SEND_MESSAGE"]
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(api_url, json=payload, headers=headers)
        if response.status_code == 200 or response.status_code == 201:
            return f"✅ Webhook configurado exitosamente: {url}"
        return f"❌ Error configurando webhook: {response.text}"

if __name__ == "__main__":
    mcp.run()
