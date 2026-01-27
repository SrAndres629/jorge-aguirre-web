import httpx
import asyncio
import sys
import os
import base64
import json

# Add current directory to path
sys.path.append(os.getcwd())

from app.config import settings

async def get_qr_debug():
    base_url = settings.EVOLUTION_API_URL
    headers = {"apikey": settings.EVOLUTION_API_KEY}
    instance = settings.EVOLUTION_INSTANCE
    
    print(f"🕵️ Debugging QR for: {instance}")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Check State
        try:
            resp = await client.get(f"{base_url}/instance/connectionState/{instance}", headers=headers)
            print(f"State Status: {resp.status_code}")
            print(f"State Body: {resp.text}")
        except Exception as e:
            print(f"State Check Failed: {e}")

        # 2. Connect / Get QR
        print(f"🔗 Requesting QR...")
        try:
            resp = await client.get(f"{base_url}/instance/connect/{instance}", headers=headers)
            print(f"Connect Status: {resp.status_code}")
            data = resp.json()
            print(f"Connect Body: {json.dumps(data, indent=2)}") 
            with open("debug_qr_output.json", "w") as f:
                json.dump(data, f, indent=2)
            print(f"Dumped to debug_qr_output.json")
            print(f"Connect Body Keys: {list(data.keys())}") 
            
            if "base64" in data:
                print("✅ Found 'base64' key.")
                qr_base64 = data["base64"]
            elif "qrcode" in data:
                 print("✅ Found 'qrcode' key.")
                 if isinstance(data["qrcode"], dict) and "base64" in data["qrcode"]:
                     qr_base64 = data["qrcode"]["base64"]
                 else:
                     qr_base64 = None
            else:
                qr_base64 = None
                
            if qr_base64:
                 if 'base64,' in qr_base64:
                    qr_base64 = qr_base64.split('base64,')[1]
                 img_data = base64.b64decode(qr_base64)
                 output_file = "whatsapp_qr.png"
                 with open(output_file, "wb") as f:
                    f.write(img_data)
                 print(f"💾 Saved to {os.path.abspath(output_file)}")
            else:
                 print(f"⚠️ NO QR DATA FOUND in response.")

        except Exception as e:
            print(f"Connect Failed: {e}")

if __name__ == "__main__":
    asyncio.run(get_qr_debug())
