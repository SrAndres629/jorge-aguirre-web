import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("EVOLUTION_API_URL", "https://evolution-whatsapp-zn13.onrender.com")
API_KEY = os.getenv("EVOLUTION_API_KEY")
INSTANCE = os.getenv("EVOLUTION_INSTANCE", "NataliaCoreProd")
PHONE = os.getenv("WHATSAPP_NUMBER", "59164714751") # Default from config

HEADERS = {
    "apikey": API_KEY,
    "Content-Type": "application/json"
}

def check_connection():
    print(f"📡 Checking Status for {INSTANCE}...")
    try:
        res = requests.get(f"{API_URL}/instance/connectionState/{INSTANCE}", headers=HEADERS)
        print(f"Status Code: {res.status_code}")
        print(f"Response: {res.text}")
        
        if res.status_code == 200:
            data = res.json()
            state = data.get("instance", {}).get("state") or data.get("state")
            if state == "open":
                print("✅ CONNECTION: OPEN (Ready)")
                return True
            else:
                 print(f"⚠️ CONNECTION: {state}")
        return False
    except Exception as e:
        print(f"❌ Error checking connection: {e}")
        return False

def send_test_message():
    print(f"📨 Sending Test Message to {PHONE}...")
    url = f"{API_URL}/message/sendText/{INSTANCE}"
    payload = {
        "number": PHONE,
        "text": "🤖 *Test de Verificación Natalia*\n\nSi lees esto: \n1. El envío funciona.\n2. La conexión es estable.\n3. Responde a este mensaje para probar la recepción."
    }
    
    try:
        res = requests.post(url, json=payload, headers=HEADERS)
        print(f"Send Result: {res.status_code}")
        if res.status_code == 201 or res.status_code == 200:
             print("✅ SEND: SUCCESS")
             print(res.json())
        else:
             print(f"❌ SEND FAILED: {res.text}")
    except Exception as e:
        print(f"❌ Error sending message: {e}")

if __name__ == "__main__":
    if check_connection():
        send_test_message()
    else:
        print("⛔ Cannot send message. Instance not open.")
