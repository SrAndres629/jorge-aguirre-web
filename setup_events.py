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
    # Confirmed Path: index -> event("") -> webhook("/webhook") -> set("/set/:instance")
    # Result: /webhook/set/{INSTANCE}
    url = f"{BASE_URL}/webhook/set/{INSTANCE}"
    
    # Payload matching webhookSchema (must be wrapped in 'webhook')
    payload = {
        "webhook": {
            "enabled": True,
            "url": NATALIA_WEBHOOK_URL,
            "webhookByEvents": True,
            "events": [
                "MESSAGES_UPSERT",
                "MESSAGES_UPDATE",
                "CONNECTION_UPDATE"
            ]
        }
    }
    
    try:
        resp = requests.post(url, json=payload, headers=HEADERS)
        if resp.status_code == 200 or resp.status_code == 201:
            print(f"{Fore.GREEN}✅ Webhook Configured: {NATALIA_WEBHOOK_URL}")
        else:
            print(f"{Fore.RED}❌ Webhook configuration failed: {resp.text}")
    except Exception as e:
        print(f"{Fore.RED}❌ Error: {e}")

def set_behavior_settings():
    print(f"{Fore.CYAN} Setting Instance Behavior (Reject Calls, etc.)...")
    # Confirmed Path: index -> settings("/settings") -> set("/set/:instance")
    # Result: /settings/set/{INSTANCE}
    url = f"{BASE_URL}/settings/set/{INSTANCE}"
    
    # Payload matching SettingsDto (strict validation requires syncFullHistory)
    payload = {
        "rejectCall": True,
        "msgCall": "🤖 Soy la IA de Jorge Aguirre. Por favor escríbeme, no puedo contestar llamadas.",
        "groupsIgnore": True,
        "alwaysOnline": True,
        "readMessages": True,
        "readStatus": False,
        "syncFullHistory": False,
    }
    
    try:
        resp = requests.post(url, json=payload, headers=HEADERS)
        if resp.status_code == 200 or resp.status_code == 201:
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

def monitor_response():
    print(f"\n{Fore.CYAN}🕵️ MONITORING CHAT FOR AI RESPONSE (60s timeout)...")
    url = f"{BASE_URL}/chat/fetchMessages/{INSTANCE}"
    params = {"number": "59178113055", "limit": 5}
    
    start_time = time.time()
    last_count = 0
    
    while time.time() - start_time < 60:
        try:
            resp = requests.get(url, headers=HEADERS, params=params)
            if resp.status_code == 200:
                msgs = resp.json()
                if isinstance(msgs, list):
                    # Filter for messages FROM the bot (fromMe=True) that are recent
                    ai_replies = [m for m in msgs if m.get('key', {}).get('fromMe') == True]
                    
                    if len(ai_replies) > last_count and last_count > 0:
                        # New reply detected
                        latest = ai_replies[0] # Usually first is newest? Check verification
                        content = latest.get('message', {}).get('conversation') or latest.get('message', {}).get('extendedTextMessage', {}).get('text')
                        print(f"\n{Fore.MAGENTA}🤖 [NATALIA REPLY DETECTED]:\n{Style.BRIGHT}{content}{Style.RESET_ALL}")
                        print(f"{Fore.GREEN}✅ INTEGRATION SUCCESSFUL: Full Loop Verified.")
                        return
                    
                    last_count = len(ai_replies)
            
            sys.stdout.write(".")
            sys.stdout.flush()
            time.sleep(3)
            
        except Exception as e:
            pass
            
    print(f"\n{Fore.YELLOW}⚠️ No AI reply detected within 60s. (Might still be processing or deploying).")

if __name__ == "__main__":
    print(f"{Fore.YELLOW}=== INTEGRATION SETUP ===")
    setup_webhook()
    time.sleep(1)
    set_behavior_settings()
    time.sleep(1)
    send_test_message()
    monitor_response()
