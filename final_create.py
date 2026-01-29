import httpx
import asyncio
import json
import webbrowser
import os

API_URL = "https://evolution-whatsapp-zn13.onrender.com"
API_KEY = "JorgeSecureKey123"
INSTANCE = "NataliaBrain"

async def final_create():
    headers = {"apikey": API_KEY, "Content-Type": "application/json"}
    print(f"🛠️ FINAL CREATE ATTEMPT FOR: {INSTANCE}")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. CREATE with EXTENDED PAYLOAD
        body = {
            "instanceName": INSTANCE,
            "token": API_KEY,
            "qrcode": True,
            "integration": "WHATSAPP-BAILEYS"
        }
        print(f"   Payload: {json.dumps(body)}")
        
        resp = await client.post(f"{API_URL}/instance/create", json=body, headers=headers)
        print(f"   Result: {resp.status_code}")
        print(f"   Response: {resp.text}")
        
        if resp.status_code == 201:
             # 2. GET QR
             print("   📸 Fetching QR Code...")
             resp = await client.get(f"{API_URL}/instance/connect/{INSTANCE}", headers=headers)
             if resp.status_code == 200:
                data = resp.json()
                b64 = data.get("base64") or data.get("code")
                if b64 and b64.startswith("data:image"):
                    b64 = b64.split(",")[1]
                
                if b64:
                    html_content = f"""
                    <html>
                    <body style="background-color: #1a1a1a; display: flex; justify-content: center; align-items: center; height: 100vh; flex-direction: column; color: white; font-family: sans-serif;">
                        <h1>🤖 Natalia Brain (Final V2)</h1>
                        <p>Scan this QR Code IMMEDIATELY.</p>
                        <div style="background: white; padding: 20px; border-radius: 10px;">
                            <img src="data:image/png;base64,{b64}" style="width: 300px; height: 300px;" />
                        </div>
                    </body>
                    </html>
                    """
                    with open("qr_final_v2.html", "w") as f:
                        f.write(html_content)
                    print("\n✅ QR CODE GENERATED: qr_final_v2.html")
                    abs_path = os.path.abspath("qr_final_v2.html")
                    webbrowser.open(f"file://{abs_path}")
             else:
                 print(f"   ❌ Connect Failed: {resp.status_code}")

if __name__ == "__main__":
    asyncio.run(final_create())
