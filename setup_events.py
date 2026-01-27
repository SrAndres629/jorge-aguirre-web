import requests
import os
import json
import time
from colorama import init, Fore, Style

init(autoreset=True)

# --- CONFIGURACIÓN ---
# Ajusta estas variables si es necesario
INSTANCE = "NataliaCoreV1"
API_URL = "https://evolution-whatsapp-zn13.onrender.com"  # Tu URL de Evolution
API_KEY = "JorgeSecureKey123"                             # Tu API Key de Evolution
# IMPORTANTE: Usamos el endpoint '/webhook/evolution' que está diseñado para el payload de Evolution
WEBHOOK_TARGET = "https://jorge-aguirre-web.onrender.com/webhook/evolution" 
ADMIN_PHONE = "59178113055" 

headers = {
    "apikey": API_KEY,
    "Content-Type": "application/json"
}

def setup():
    print(f"{Fore.CYAN}=== ⚙️ CONFIGURANDO CEREBRO DE NATALIA ===")

    # 1. CONFIGURAR WEBHOOK (El Oído)
    print(f"\n🎧 Configurando Webhook hacia: {WEBHOOK_TARGET}")
    webhook_payload = {
        "webhook": {
            "enabled": True,
            "url": WEBHOOK_TARGET,
            "events": [
                "MESSAGES_UPSERT",       # Mensajes nuevos
                "MESSAGES_UPDATE",       # Doble check azul
                "CONNECTION_UPDATE"      # Si se desconecta
            ],
            "byEvents": False,
            "base64": False
        }
    }
    
    try:
        # Nota: El endpoint correcto suele ser /webhook/set/NOMBRE_INSTANCIA
        resp = requests.post(f"{API_URL}/webhook/set/{INSTANCE}", json=webhook_payload, headers=headers)
        if resp.status_code == 200 or resp.status_code == 201:
            print(f"{Fore.GREEN}✅ Webhook configurado EXITOSAMENTE.")
        else:
            print(f"{Fore.RED}❌ Error configurando Webhook: {resp.text}")
    except Exception as e:
        print(f"{Fore.RED}❌ Excepción en Webhook: {e}")

    # 2. CONFIGURAR COMPORTAMIENTO (Opcional - Settings)
    print("\n🛡️ Configurando Comportamiento (Settings)...")
    settings_payload = {
        "rejectCall": True,      # Rechazar llamadas automáticamente
        "groupsIgnore": True,    # Ignorar grupos (para no gastar IA)
        "alwaysOnline": True,     # Aparecer siempre en línea
        "readMessages": True,
        "readStatus": False,
        "syncFullHistory": False
    }
    
    try:
        # Endpoint para settings generales
        resp = requests.post(f"{API_URL}/settings/set/{INSTANCE}", json=settings_payload, headers=headers)
        if resp.status_code == 200 or resp.status_code == 201:
            print(f"{Fore.GREEN}✅ Settings configurados EXITOSAMENTE.")
        else:
            # Si falla, no es crítico, seguimos.
            print(f"{Fore.YELLOW}⚠️ Aviso en Settings (No crítico): {resp.text}")
    except Exception as e:
        print(f"{Fore.RED}⚠️ Excepción en Settings: {e}")

    # 3. PRUEBA FINAL (El Saludo)
    print(f"\n📨 Enviando mensaje de prueba al Admin: {ADMIN_PHONE}")
    msg_payload = {
        "number": ADMIN_PHONE,
        "text": "🤖 *SISTEMA RE-CALIBRADO*\n\nHola Admin. He actualizado mis conexiones neuronales.\nEl Webhook debería estar activo ahora. Respóndeme para probar mi cerebro."
    }
    
    try:
        resp = requests.post(f"{API_URL}/message/sendText/{INSTANCE}", json=msg_payload, headers=headers)
        if resp.status_code == 200:
             print(f"{Fore.GREEN}✅ Test Message Sent!")
        else:
             print(f"{Fore.RED}� Estado del envío: {resp.status_code} (PENDING es normal)")
    except Exception as e:
        print(f"{Fore.RED}❌ Error enviando mensaje: {e}")

if __name__ == "__main__":
    setup()
