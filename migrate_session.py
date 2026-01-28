import os
import time
import requests
import base64
from dotenv import load_dotenv

# 1. Load Environment
load_dotenv()

API_URL = os.getenv("EVOLUTION_API_URL", "https://evolution-whatsapp-zn13.onrender.com")
API_KEY = os.getenv("EVOLUTION_API_KEY")

# Check credentials
if not API_KEY:
    print("❌ ERROR: EVOLUTION_API_KEY not found in .env")
    API_KEY = input("👉 Enter your Evolution API KEY manually: ").strip()

HEADERS = {
    "apikey": API_KEY,
    "Content-Type": "application/json"
}

OLD_INSTANCE = "NataliaCoreV1"
NEW_INSTANCE = "NataliaCoreProd"

def log(msg, emoji="ℹ️"):
    print(f"{emoji} {msg}")

def delete_instance(instance_name):
    log(f"Checking for existing instance: {instance_name}...")
    try:
        # Check status first
        check = requests.get(f"{API_URL}/instance/connectionState/{instance_name}", headers=HEADERS)
        if check.status_code == 404:
            log(f"Instance {instance_name} does not exist. Clean.", "✅")
            return
        
        # Logout/Delete
        log(f"Deleting {instance_name}...", "🗑️")
        url = f"{API_URL}/instance/logout/{instance_name}"
        requests.delete(url, headers=HEADERS)
        
        # Wait for deletion
        time.sleep(2)
        
        # Force Delete from DB if Logout wasn't enough (Evolution specific)
        url_del = f"{API_URL}/instance/delete/{instance_name}"
        requests.delete(url_del, headers=HEADERS)
        log(f"Deleted {instance_name} successfully.", "✅")
        
    except Exception as e:
        log(f"Error checking/deleting {instance_name}: {e}", "⚠️")

def create_instance(instance_name):
    log(f"Creating new instance: {instance_name}...", "🏗️")
    payload = {
        "instanceName": instance_name,
        "token": instance_name, # Usually just needs to be unique
        "qrcode": True,
        "integration": "WHATSAPP-BAILEYS"
    }
    
    try:
        # 1. Create
        url = f"{API_URL}/instance/create"
        res = requests.post(url, json=payload, headers=HEADERS)
        
        if res.status_code == 403: # Already exists
            log(f"Instance {instance_name} already exists. Fetching QR...", "⚠️")
        elif res.status_code not in [200, 201]:
             log(f"Failed to create instance: {res.text}", "❌")
             return False
        
        # 2. Get QR Code
        log("Fetching QR Code...", "📷")
        time.sleep(1) 
        url_qr = f"{API_URL}/instance/connect/{instance_name}"
        res_qr = requests.get(url_qr, headers=HEADERS)
        
        if res_qr.status_code == 200:
            data = res_qr.json()
            if "base64" in data:
                b64_str = data["base64"].replace("data:image/png;base64,", "")
                with open("whatsapp_qr.png", "wb") as f:
                    f.write(base64.b64decode(b64_str))
                log(f"QR Code saved to: {os.path.abspath('whatsapp_qr.png')}", "✅")
                print("\n📱 SCAN 'whatsapp_qr.png' WITH YOUR PHONE NOW.\n")
                return True
            else:
                # Maybe already connected?
                if "instance" in data and data["instance"].get("state") == "open":
                     log("Instance is ALREADY CONNECTED! No QR needed.", "🎉")
                     return True
                log(f"No QR in response: {data}", "❓")
        else:
             log(f"Failed to fetch QR: {res_qr.text}", "❌")
             
    except Exception as e:
        log(f"Creation failed: {e}", "❌")
    
    return False

def main():
    print(f"\n🧠 [SESSION MIGRATION] {OLD_INSTANCE} -> {NEW_INSTANCE}\nTarget: {API_URL}\n")
    
    # 1. Purge Old
    delete_instance(OLD_INSTANCE)
    
    # 2. Ensure New Exists & Get QR
    create_instance(NEW_INSTANCE)

if __name__ == "__main__":
    main()
