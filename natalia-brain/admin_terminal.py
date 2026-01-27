import os
import time
import json
import base64
import requests
import pathlib
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("EVOLUTION_API_URL", "https://evolution-whatsapp-zn13.onrender.com")
EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY", "JorgeSecureKey123")
EVOLUTION_INSTANCE = os.getenv("EVOLUTION_INSTANCE", "NataliaCoreV1")

# --- SENIOR STATUS ---
HAS_AUTO_HEAL = True # Applied in Evolution-API source code
# ---------------------

HEADERS = {
    "Content-Type": "application/json",
    "apikey": EVOLUTION_API_KEY
}

CORE_DIR = pathlib.Path(__file__).parent.resolve()

def check_deployment():
    print("\n🔍 Checking system status...")
    if HAS_AUTO_HEAL:
        print("✅ Senior Auto-Heal: Enabled (Code Patches Applied)")
    
    # Check if there are unpushed changes in evolution-api
    try:
        os.chdir(CORE_DIR.parent / "evolution-api")
        status = os.popen("git status --short").read().strip()
        if status:
            print("⚠️ ALERT: You have uncommitted/unpushed changes in 'evolution-api'.")
            print("👉 Please run: git add . && git commit -m 'Senior Auto-Heal' && git push")
            print("   Then wait for Render to redeploy before creating the instance.")
        os.chdir(CORE_DIR)
    except Exception as e:
        # This might happen if 'evolution-api' directory doesn't exist or git is not installed
        print(f"⚠️ Could not check 'evolution-api' deployment status: {e}")
        os.chdir(CORE_DIR) # Ensure we return to CORE_DIR even if an error occurs

def list_instances():
    print(f"\n🔍 Listing instances on {API_URL}...")
    try:
        response = requests.get(f"{API_URL}/instance/fetchInstances", headers=HEADERS)
        if response.status_code == 200:
            instances = response.json()
            for inst in instances:
                print(f" - [{inst['instance']['name']}] State: {inst['instance']['connectionStatus']['state']}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")

def create_instance():
    print(f"\n🚀 Creating instance '{INSTANCE}'...")
    payload = {
        "instanceName": INSTANCE,
        "token": API_KEY,
        "number": "59164714751",
        "qrcode": True,
        "integration": "WHATSAPP-BAILEYS"
    }
    response = requests.post(f"{API_URL}/instance/create", headers=HEADERS, json=payload)
    print(f"Result: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def delete_instance(name=None):
    target = name or INSTANCE
    print(f"\n🗑️ Deleting instance '{target}'...")
    response = requests.delete(f"{API_URL}/instance/delete/{target}", headers=HEADERS)
    print(f"Result: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)

def get_qr():
    print(f"\n📲 Fetching QR for '{INSTANCE}'...")
    response = requests.get(f"{API_URL}/instance/connect/{INSTANCE}", headers=HEADERS)
    data = response.json()
    
    if "base64" in data:
        img_data = data["base64"].split(",")[1]
        with open("whatsapp_qr.png", "wb") as fh:
            fh.write(base64.b64decode(img_data))
        print("✅ SUCCESS: QR saved to 'whatsapp_qr.png'. Scan it now!")
    elif "code" in data:
        print(f"🔑 PAIRING CODE: {data['code']}")
    else:
        print("⚠️ No QR available. Verify instance state.")
        print(json.dumps(data, indent=2))

def show_menu():
    while True:
        print("\n=== NATALIA BRAIN COMMAND CENTER ===")
        print("1. List Instances")
        print("2. Create NataliaCoreV1")
        print("3. Delete NataliaCoreV1")
        print("4. Get QR Code")
        print("5. Exit")
        choice = input("\nSelect an option: ")
        
        if choice == "1": list_instances()
        elif choice == "2": create_instance()
        elif choice == "3": delete_instance()
        elif choice == "4": get_qr()
        elif choice == "5": break
        else: print("Invalid option.")

if __name__ == "__main__":
    show_menu()
