import asyncio
import httpx
import logging
from app.config import settings

# Configure specialized logger
logger = logging.getLogger("watchdog")
logging.basicConfig(level=logging.INFO)

async def start_watchdog():
    """
    Antigravity Watchdog 🛡️
    Runs in background to ensure NataliaBrain stays connected.
    Cycle: Every 5 minutes.
    """
    logger.info("🛡️ Watchdog System Active. Guarding: %s", settings.EVOLUTION_INSTANCE)
    
    while True:
        try:
            await check_connection_health()
        except Exception as e:
            logger.error(f"❌ Watchdog Error: {e}")
            
        # Wait 5 minutes before next check
        await asyncio.sleep(300)

async def check_connection_health():
    headers = {
        "apikey": settings.EVOLUTION_API_KEY,
        "Content-Type": "application/json"
    }
    
    # 2. Check Status
    target_url = f"{settings.EVOLUTION_API_URL}/instance/connectionState/{settings.EVOLUTION_INSTANCE}"
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            resp = await client.get(target_url, headers=headers)
            
            if resp.status_code == 200:
                data = resp.json()
                # Evolution v2 often nests in 'instance' -> 'state'
                # Or sometimes directly 'state' depending on exact version. 
                # Handling both safely.
                state = "unknown"
                if "instance" in data and isinstance(data["instance"], dict):
                     state = data["instance"].get("state", "unknown")
                elif "state" in data:
                     state = data["state"]
                
                if state == "open":
                    logger.info("✅ System Healthy. Connection: OPEN")
                elif state == "close" or state == "connecting":
                    logger.warning(f"⚠️ Connection Lost ({state}). Attempting Reconnect...")
                    await attempt_reconnect(client, headers)
                else:
                    logger.warning(f"⚠️ Status Unknown/Refused: {state}")

            elif resp.status_code == 404:
                 logger.error("🚨 Critical Failure: Instance NOT FOUND. (Human Intervention Required)")
            else:
                 logger.warning(f"⚠️ Watchdog Poll Failed: {resp.status_code}")
                 
        except httpx.RequestError as e:
             logger.error(f"❌ Network unreachable: {e}")

async def attempt_reconnect(client, headers):
    reconnect_url = f"{settings.EVOLUTION_API_URL}/instance/connect/{settings.EVOLUTION_INSTANCE}"
    try:
        resp = await client.get(reconnect_url, headers=headers)
        logger.info(f"🔄 Reconnect Signal Sent. Status: {resp.status_code}")
    except Exception as e:
        logger.error(f"❌ Fix Failed: {e}")
