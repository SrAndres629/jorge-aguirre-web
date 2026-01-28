import requests
import json
import time

# --- CONFIGURACIÓN ---
INSTANCE = "NataliaCoreV1"
EVOLUTION_URL = "https://evolution-whatsapp-zn13.onrender.com"
API_KEY = "JorgeSecureKey123"
# URL CORRECTA DE TU CEREBRO (Verifica que no tenga espacios extra)
BRAIN_URL = "https://natalia-brain.onrender.com/webhook/evolution" 

headers = {
    "apikey": API_KEY,
    "Content-Type": "application/json"
}

def fix_webhook():
    print(f"🔧 INICIANDO PROTOCOLO DE REPARACIÓN DE AUDICIÓN (WEBHOOK)")
    print(f"🎯 Target Brain: {BRAIN_URL}")

    # ESTRATEGIA A: Endpoint directo de Webhook (Formato Estándar)
    payload_a = {
        "webhook": {
            "enabled": True,
            "url": BRAIN_URL,
            "events": ["MESSAGES_UPSERT", "MESSAGES_UPDATE", "CONNECTION_UPDATE"],
            "byEvents": False,
            "base64": False
        }
    }
    
    print("\n👉 INTENTO A: /webhook/set/ (Payload Anidado)")
    try:
        resp = requests.post(f"{EVOLUTION_URL}/webhook/set/{INSTANCE}", json=payload_a, headers=headers)
        print(f"   Status: {resp.status_code} | Resp: {resp.text}")
        if resp.status_code == 200:
            return True
    except Exception as e:
        print(f"   Error: {e}")

    # ESTRATEGIA B: Habilitar webhook en opciones de instancia (A veces necesario antes de configurar URL)
    print("\n👉 INTENTO B: /instance/setSettings/ (Habilitar flag)")
    payload_b = {
        "webhook": {
             "enabled": True,
             "url": BRAIN_URL
        }
    }
    try:
        resp = requests.post(f"{EVOLUTION_URL}/instance/setSettings/{INSTANCE}", json=payload_b, headers=headers)
        print(f"   Status: {resp.status_code} | Resp: {resp.text}")
    except Exception as e:
        print(f"   Error: {e}")

    # ESTRATEGIA C: Búsqueda del Webhook actual para confirmar
    print("\n🔍 VERIFICACIÓN FINAL: /webhook/find/")
    try:
        resp = requests.get(f"{EVOLUTION_URL}/webhook/find/{INSTANCE}", headers=headers)
        data = resp.json()
        # Handle various response formats
        current_url = None
        if "url" in data:
            current_url = data["url"]
        elif "webhook" in data and "url" in data["webhook"]:
             current_url = data["webhook"]["url"]
        
        print(f"   Webhook Actual detectado: {current_url}")

        if current_url == BRAIN_URL:
            print("✅ ÉXITO TOTAL: El webhook apunta al Cerebro Correcto.")
            return True
        else:
            print(f"❌ FALLO: El webhook actual es: {current_url}")
            return False
    except Exception as e:
        print(f"   Error verificando: {e}")
        return False

if __name__ == "__main__":
    fix_webhook()
