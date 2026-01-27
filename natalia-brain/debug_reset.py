import httpx
import asyncio
import sys
import os
import base64

# Add current directory to path
sys.path.append(os.getcwd())

from app.config import settings

async def reset_workflow():
    base_url = settings.EVOLUTION_API_URL
    headers = {"apikey": settings.EVOLUTION_API_KEY}
    instance = settings.EVOLUTION_INSTANCE
    
    print(f"☢️  NUCLEAR RESET for Instance: {instance}")
    print(f"Target: {base_url}")
    print("-" * 50)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. DELETE
        print(f"🔥 Deleting {instance}...")
        try:
            resp = await client.delete(f"{base_url}/instance/delete/{instance}", headers=headers)
            print(f"Delete Status: {resp.status_code}")
            print(f"Delete Body: {resp.text}")
        except Exception as e:
            print(f"Delete Failed: {e}")

        await asyncio.sleep(15)
        
        # 2. CREATE
        print(f"✨ Creating {instance}...")
        payload = {
            "instanceName": instance, 
            "token": settings.EVOLUTION_API_KEY,
            "qrcode": True,
            "integration": "WHATSAPP-BAILEYS" 
        }
        try:
            resp = await client.post(f"{base_url}/instance/create", json=payload, headers=headers)
            print(f"Create Status: {resp.status_code}")
            print(f"Create Body: {resp.text}")
        except Exception as e:
            print(f"Create Failed: {e}")
            
        await asyncio.sleep(2)

        # 3. CONNECT / QR
        print(f"🔗 Connecting to get QR...")
        try:
            resp = await client.get(f"{base_url}/instance/connect/{instance}", headers=headers)
            print(f"Connect Status: {resp.status_code}")
            data = resp.json()
            
            qr_base64 = None
            if "base64" in data:
                qr_base64 = data["base64"]
            elif "qrcode" in data and "base64" in data["qrcode"]:
                 qr_base64 = data["qrcode"]["base64"]
                 
            if qr_base64:
                 if 'base64,' in qr_base64:
                    qr_base64 = qr_base64.split('base64,')[1]
                 img_data = base64.b64decode(qr_base64)
                 output_file = "whatsapp_qr.png"
                 with open(output_file, "wb") as f:
                    f.write(img_data)
                 print(f"✅ QR Code saved to {output_file}")
            else:
                 print(f"⚠️ No QR in response: {str(data)[:100]}")

        except Exception as e:
            print(f"Connect Failed: {e}")

if __name__ == "__main__":
    asyncio.run(reset_workflow())
