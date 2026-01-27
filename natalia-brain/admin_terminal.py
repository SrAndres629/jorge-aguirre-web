import os
import time
import json
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("EVOLUTION_API_URL", "https://evolution-whatsapp-zn13.onrender.com")
API_KEY = os.getenv("EVOLUTION_API_KEY", "JorgeSecureKey123")
INSTANCE = os.getenv("EVOLUTION_INSTANCE", "NataliaCoreV1")

HEADERS = {
    "Content-Type": "application/json",
    "apikey": API_KEY
}

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
        "qrcode": True
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
