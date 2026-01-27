import requests
import time
import json
import base64
import sys
import os
from io import BytesIO
from colorama import init, Fore, Style
from PIL import Image

# Initialize Colorama
init(autoreset=True)

# ==========================================
# CONFIGURATION
# ==========================================
BASE_URL = "https://evolution-whatsapp-zn13.onrender.com"
API_KEY = "JorgeSecureKey123"
INSTANCE_NAME = "NataliaCoreV1"

HEADERS = {
    "apikey": API_KEY,
    "Content-Type": "application/json"
}

# ==========================================
# ASCII QR LOGIC
# ==========================================
def print_qr_ascii(base64_str):
    """Converts Base64 Image to ASCII QR for Terminal"""
    try:
        if "base64," in base64_str:
            base64_str = base64_str.split("base64,")[1]
        
        image_data = base64.b64decode(base64_str)
        image = Image.open(BytesIO(image_data))
        
        # Resize for terminal (QR codes are usually square)
        # We need small enough to fit, but large enough to scan.
        # WhatsApp QRs are complex, so pixel-perfect mapping is best.
        # But terminal fonts are rectangular (height > width).
        
        # Better approach: Iterate pixels directly if size allows.
        # Assuming standard QR size.
        img = image.convert('L') # Grayscale
        width, height = img.size
        
        # Terminal optimization: Use block char '▀' to represent two vertical pixels?
        # Or just standard full block '██' for black.
        
        # Simple robust approach: 1 pixel = 2 char width '  ' vs '██'
        # Because terminal chars are tall.
        
        print("\n" * 2)
        sys.stdout.write("QUIET ZONE (WHITE BUFFER)\n")
        
        # Thresholding
        threshold = 128
        
        # Creating border
        border = 4
        
        # Scale down significantly for terminal
        # Standard WhatsApp QR is ~264x264. Terminal char is tall.
        # Target width ~45 chars.
        base_width = 45
        w_percent = (base_width / float(width))
        h_size = int((float(height) * float(w_percent)))
        
        img = img.resize((base_width, h_size), Image.Resampling.LANCZOS)
        width, height = img.size

        for y in range(height):
            line = ""
            for x in range(width):
                pixel = img.getpixel((x, y))
                if pixel < threshold:
                    line += "██" # Black
                else:
                    line += "  " # White
            print(f"{Fore.WHITE}{line}{Style.RESET_ALL}")
            
        print("\n" * 2)
        print(f"{Fore.CYAN}👉 SCAN THIS CODE WITH WHATSAPP LINKED DEVICES{Style.RESET_ALL}")
        
    except Exception as e:
        print(f"{Fore.RED}❌ Error rendering ASCII QR: {e}")

# ==========================================
# STATE MACHINE LOGIC
# ==========================================
def api_request(method, endpoint, data=None):
    url = f"{BASE_URL}/{endpoint}"
    try:
        if method == "GET":
            return requests.get(url, headers=HEADERS, timeout=10)
        elif method == "POST":
            return requests.post(url, json=data, headers=HEADERS, timeout=10)
    except Exception as e:
        print(f"{Fore.RED}⚠️ Network Error: {e}")
        return None

def check_connection_state():
    resp = api_request("GET", f"instance/connectionState/{INSTANCE_NAME}")
    if resp and resp.status_code == 200:
        data = resp.json()
        state = data.get("instance", {}).get("state", "unknown")
        return state
    return "unknown"

def main():
    print(f"{Fore.GREEN}==================================================")
    print(f"{Fore.GREEN}🤖 NATALIA CORE - CONNECTION TERMINAL V2.0")
    print(f"{Fore.GREEN}==================================================")
    
    # 1. EXISTENCE PROOF
    print(f"{Fore.YELLOW}[LOGIC] Verifying Instance Existence...")
    resp = api_request("GET", "instance/fetchInstances")
    
    exists = False
    if resp and resp.status_code == 200:
        instances = resp.json()
        if isinstance(instances, list):
             exists = any(i.get('instance', {}).get('instanceName') == INSTANCE_NAME for i in instances)
    
    if exists:
        print(f"{Fore.GREEN}✅ Instance '{INSTANCE_NAME}' found.")
    else:
        print(f"{Fore.YELLOW}⚠️ Instance not found in list. Attempting creation...")
        create_resp = api_request("POST", "instance/create", {
            "instanceName": INSTANCE_NAME,
            "qrcode": True,
            "integration": "WHATSAPP-BAILEYS"
        })
        
        if create_resp:
            if create_resp.status_code == 201:
                print(f"{Fore.GREEN}✅ Instance Created Successfully.")
            elif create_resp.status_code == 403:
                # Handle "Already in use" logic
                if "already in use" in create_resp.text:
                    print(f"{Fore.GREEN}✅ Instance already exists (State 403 Confirmed).")
                else:
                     print(f"{Fore.RED}❌ Creation Failed: {create_resp.text}")
                     return
            else:
                print(f"{Fore.RED}❌ Creation Error: {create_resp.text}")
                return

    # 1.5 FORCE RESET IF STUCK
    print(f"{Fore.YELLOW}[LOGIC] Checking for stuck sessions...")
    initial_state = check_connection_state()
    if initial_state == "connecting":
        print(f"{Fore.RED}⚠️ Instance is stuck in 'connecting'. Forcing Logout to reset...")
        api_request("DELETE", f"instance/logout/{INSTANCE_NAME}")
        print(f"{Fore.GREEN}✅ Logout command sent. Waiting 5s...")
        time.sleep(5)

    # 2. MONITORING LOOP
    print(f"{Fore.CYAN}[LOOP] Entering Real-time Monitoring Loop...")
    
    while True:
        state = check_connection_state()
        
        if state == "open":
            print(f"\n{Fore.GREEN}✅✅✅ CONNECTED! NATALIA IS ONLINE. ✅✅✅")
            break
            
        if state == "open":
            print(f"\n{Fore.GREEN}✅✅✅ CONNECTED! NATALIA IS ONLINE. ✅✅✅")
            break
            
        # Treat 'connecting' as needing a QR scan too (common behavior)
        elif state == "close" or state == "unknown" or state == "connecting":
            print(f"\n{Fore.MAGENTA}🔄 Fetching QR Code (State: {state})...")
            qr_resp = api_request("GET", f"instance/connect/{INSTANCE_NAME}")
            
            if qr_resp and qr_resp.status_code == 200:
                data = qr_resp.json()
                base64_qr = data.get('base64') or (data.get('qrcode', {}).get('base64'))
                
                if base64_qr:
                    # Clear screen kind of
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print_qr_ascii(base64_qr)
                    print(f"{Fore.YELLOW}⏱️  Auto-refresh in 15 seconds... (Scan now!)")
                    
                    # Wait for scan loop
                    for i in range(15):
                        time.sleep(1)
                        # Check status during wait to exit fast
                        # Don't check every second to avoid rate limits, maybe every 2s
                        if i % 2 == 0:
                            live_state = check_connection_state()
                            if live_state == "open":
                                break
                else:
                    if state == "connecting":
                         sys.stdout.write(f"\r{Fore.YELLOW}🔄 Connecting (Waiting for QR)...")
                         sys.stdout.flush()
                         time.sleep(2)
                    else:
                        print(f"{Fore.RED}❌ No QR data received. Waiting...")
                        time.sleep(5)
            else:
                 print(f"{Fore.RED}❌ Error fetching QR. Retrying...")
                 time.sleep(5)
        else:
             print(f"Unknown State: {state}")
             time.sleep(5)

if __name__ == "__main__":
    main()
