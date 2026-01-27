import requests
import json
import time
from colorama import init, Fore, Style

init(autoreset=True)

# CONFIG
BASE_URL = "https://evolution-whatsapp-zn13.onrender.com"
API_KEY = "JorgeSecureKey123"
INSTANCE = "NataliaCoreV1"
NATALIA_WEBHOOK_URL = "https://natalia-brain-zn13.onrender.com/webhook/evolution"

HEADERS = {
    "apikey": API_KEY,
    "Content-Type": "application/json"
}

def setup_webhook():
    print(f"{Fore.CYAN} Configuring Webhook for {INSTANCE}...")
    url = f"{BASE_URL}/webhook/set/{INSTANCE}"
    
    payload = {
        "webhookUrl": NATALIA_WEBHOOK_URL,
        "webhookByEvents": True,
        "events": [
            "MESSAGES_UPSERT",
            "MESSAGES_UPDATE",
            "CONNECTION_UPDATE"
        ],
        "enabled": True
    }
    
    try:
        resp = requests.post(url, json=payload, headers=HEADERS)
        if resp.status_code == 200:
            print(f"{Fore.GREEN}✅ Webhook Configured: {NATALIA_WEBHOOK_URL}")
        else:
            print(f"{Fore.RED}❌ Webhook configuration failed: {resp.text}")
    except Exception as e:
        print(f"{Fore.RED}❌ Error: {e}")

def set_behavior_settings():
    print(f"{Fore.CYAN} Setting Instance Behavior (Reject Calls, etc.)...")
    url = f"{BASE_URL}/instance/setSettings/{INSTANCE}"
    
    payload = {
        "reject_call": True,              # Reject calls so AI isn't interrupted
        "msg_call": "🤖 Soy la IA de Jorge Aguirre. Por favor escríbeme, no puedo contestar llamadas.",
        "groups_ignore": True,            # Ignore group messages usually
        "always_online": True,             # Keep status online
        "read_messages": True,             # Blue ticks
        "read_status": False              # Don't watch statuses
    }
    
    try:
        resp = requests.post(url, json=payload, headers=HEADERS)
        if resp.status_code == 200:
             print(f"{Fore.GREEN}✅ Settings Applied (Reject Calls: ON, Always Online: ON)")
        else:
             print(f"{Fore.RED}❌ Settings failed: {resp.text}")
             
    except Exception as e:
        print(f"{Fore.RED}❌ Error: {e}")

def send_test_message():
    print(f"{Fore.CYAN} Sending Initial Test Message to Admin Root (+59178113055)...")
    url = f"{BASE_URL}/message/sendText/{INSTANCE}"
    
    payload = {
        "number": "59178113055",
        "text": "🤖 *SISTEMA INICIADO*\n\nHola Root Admin 59178113055.\nSoy Natalia (v3.0). Estoy conectada y escuchando todos los eventos.\n\nEscríbeme algo para verificar mi lógica."
    }
    
    try:
        resp = requests.post(url, json=payload, headers=HEADERS)
        if resp.status_code == 200:
            print(f"{Fore.GREEN}✅ Test Message Sent!")
        else:
             print(f"{Fore.RED}❌ Failed to send test: {resp.text}")
    except Exception as e:
        print(f"{Fore.RED}❌ Error sending test: {e}")

if __name__ == "__main__":
    print(f"{Fore.YELLOW}=== INTEGRATION SETUP ===")
    setup_webhook()
    time.sleep(1)
    set_behavior_settings()
    time.sleep(1)
    send_test_message()
