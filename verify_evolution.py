import requests
import time
import json
import base64
import os
import webbrowser

# ==========================================
# CONFIGURACIÓN (PEGAR TU API KEY AQUÍ)
# ==========================================
BASE_URL = "https://evolution-whatsapp-zn13.onrender.com"
# ¡IMPORTANTE! Pega tu API Key abajo donde dice "PEGAR_AQUI_TU_API_KEY"
API_KEY = "JorgeSecureKey123" 
INSTANCE_NAME = "NataliaCoreV1"

HEADERS = {
    "apikey": API_KEY,
    "Content-Type": "application/json"
}

def print_step(step, msg):
    print(f"\n[PASO {step}] {msg}")

def check_instance():
    print_step(1, f"Verificando si la instancia '{INSTANCE_NAME}' existe...")
    try:
        url = f"{BASE_URL}/instance/fetchInstances"
        response = requests.get(url, headers=HEADERS)
        
        if response.status_code == 403:
            print("❌ ERROR DE AUTENTICACIÓN: Tu API Key es incorrecta o no tienes acceso.")
            return False
            
        data = response.json()
        instances = data if isinstance(data, list) else data.get('instances', [])
        
        exists = any(inst.get('instance', {}).get('instanceName') == INSTANCE_NAME for inst in instances)
        
        if exists:
            print(f"✅ La instancia '{INSTANCE_NAME}' ya existe.")
            return True
        else:
            print(f"ℹ️ La instancia '{INSTANCE_NAME}' NO existe. Necesitamos crearla.")
            return False
    except Exception as e:
        print(f"❌ Error conectando al servidor: {e}")
        return False

def create_instance():
    print_step(2, f"Creando instancia '{INSTANCE_NAME}'...")
    url = f"{BASE_URL}/instance/create"
    payload = {
        "instanceName": INSTANCE_NAME,
        "token": "", # Opcional
        "qrcode": True,
        "integration": "WHATSAPP-BAILEYS"
    }
    
    try:
        response = requests.post(url, json=payload, headers=HEADERS)
        if response.status_code == 201:
            print("✅ Instancia creada exitosamente.")
            return True
        else:
            print(f"❌ Error creando instancia: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error en la creación: {e}")
        return False

def get_qr():
    print_step(3, "Obteniendo código QR para escanear en WhatsApp...")
    url = f"{BASE_URL}/instance/connect/{INSTANCE_NAME}"
    
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            # Evolution a veces devuelve la imagen en base64 o solo el string
            qr_base64 = data.get('base64')
            
            if qr_base64:
                # Limpiar el prefijo si existe
                if "base64," in qr_base64:
                    qr_base64 = qr_base64.split("base64,")[1]
                
                # Guardar imagen temporalmente
                img_path = "whatsapp_qr.png"
                with open(img_path, "wb") as fh:
                    fh.write(base64.b64decode(qr_base64))
                
                print(f"✅ QR recibido! Abriendo imagen automáticamente...")
                webbrowser.open(f"file://{os.path.abspath(img_path)}")
                print("👉 Escanea el código QR con tu celular AHORA (Configuración -> Dispositivos vinculados).")
            else:
                print("⚠️ No se recibió imagen base64. Respuesta:", data)
        else:
            print(f"❌ Error obteniendo QR: {response.text}")
    except Exception as e:
        print(f"❌ Error obteniendo QR: {e}")

def main():
    print("==================================================")
    print("🤖 EVOLUTION API - VERIFICADOR Y CONECTOR")
    print("==================================================")
    
    if API_KEY == "PEGAR_AQUI_TU_API_KEY":
        print("❌ ALERTA: No has configurado tu API KEY en el script.")
        print("1. Abre este archivo (verify_evolution.py).")
        print("2. Busca la línea: API_KEY = 'PEGAR_AQUI_TU_API_KEY'")
        print("3. Reemplaza con tu AUTHENTICATION_API_KEY de Render.")
        return

    is_created = check_instance()
    
    if not is_created:
        success = create_instance()
        if not success:
            return
    
    # Intentar obtener el QR
    get_qr()
    
    print("\n✅ Proceso finalizado. Si escaneaste el QR, tu instancia debería estar conectada.")
    print("💡 TIP: Render puede tardar unos segundos en 'despertar' después del sleep.")

if __name__ == "__main__":
    main()
