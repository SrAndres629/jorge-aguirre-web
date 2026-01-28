import httpx
import asyncio
import os
import sys

# Configuration - HARDCODED for Reliability
API_URL = "https://evolution-whatsapp-zn13.onrender.com"
API_KEY = "JorgeSecureKey123"
INSTANCE = "NataliaCoreV1"

async def emergency_reset():
    print(f"🚨 INITIATING EMERGENCY RESET FOR: {INSTANCE}")
    print(f"Target: {API_URL}")
    
    headers = {
        "apikey": API_KEY,
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. DELETE INSTANCE
        print("\n🗑️  Step 1: Deleting Instance...")
        try:
            resp = await client.delete(f"{API_URL}/instance/delete/{INSTANCE}", headers=headers)
            print(f"Status: {resp.status_code} | Output: {resp.text}")
        except Exception as e:
            print(f"❌ Delete failed (might not exist): {e}")

        # 2. CREATE INSTANCE
        print("\n✨ Step 2: Creating New Instance...")
        payload = {
            "instanceName": INSTANCE,
            "token": API_KEY, # Using API Key as token per convention
            "qrcode": True,
            "integration": "WHATSAPP-BAILEYS"
        }
        try:
            resp = await client.post(f"{API_URL}/instance/create", json=payload, headers=headers)
            print(f"Status: {resp.status_code} | Output: {resp.text}")
            resp.raise_for_status()
        except Exception as e:
            print(f"❌ Create failed: {e}")
            return

        # 3. CONNECT / GET QR
        print("\n🔗 Step 3: Fetching QR Code...")
        try:
            resp = await client.get(f"{API_URL}/instance/connect/{INSTANCE}", headers=headers)
            data = resp.json()
            
            qr_base64 = None
            if "base64" in data:
                qr_base64 = data["base64"]
            elif "qrcode" in data and "base64" in data["qrcode"]:
                qr_base64 = data["qrcode"]["base64"]
            
            if qr_base64:
                # Save to HTML file for user to open
                html_content = f"""
                <html>
                <body style='background-color: #222; display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100vh; font-family: sans-serif; color: white;'>
                    <h1>📲 Escanea Ahora</h1>
                    <p>Instancia: {INSTANCE}</p>
                    <img src='{qr_base64}' style='border: 10px solid white; border-radius: 10px;' />
                    <p>Una vez escaneado, el bot se reiniciará automáticamente.</p>
                </body>
                </html>
                """
                with open("nuevo_qr.html", "w", encoding="utf-8") as f:
                    f.write(html_content)
                
                print("✅ QR Code saved to 'nuevo_qr.html'")
                # Try to open it
                import webbrowser
                webbrowser.open("nuevo_qr.html")
            else:
                print("⚠️ No QR returned. Instance might be already connected?")
                print(f"Response: {data}")

        except Exception as e:
            print(f"❌ Connect failed: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(emergency_reset())
    except Exception as e:
        print(f"Fatal Check: {e}")
