import httpx
import asyncio
import webbrowser
import os
import json

API_URL = "https://evolution-whatsapp-zn13.onrender.com"
API_KEY = "JorgeSecureKey123"
INSTANCE = "NataliaBrain"

async def fetch_qr():
    headers = {"apikey": API_KEY, "Content-Type": "application/json"}
    print(f"📸 FETCHING QR FOR: {INSTANCE}")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(f"{API_URL}/instance/connect/{INSTANCE}", headers=headers)
        
        if resp.status_code == 200:
            data = resp.json()
            b64 = data.get("base64") or data.get("code")
            
            if b64:
                if b64.startswith("data:image"):
                    b64 = b64.split(",")[1]
                
                print(f"✅ QR Data Length: {len(b64)}")
                
                html_content = f"""
                <html>
                <body style="background-color: #1a1a1a; display: flex; justify-content: center; align-items: center; height: 100vh; flex-direction: column; color: white; font-family: sans-serif;">
                    <h1>🤖 Natalia Brain (Clean Reset)</h1>
                    <p>Status: {data.get('instance', {}).get('state')}</p>
                    <p>Scan this QR Code to Link.</p>
                    <div style="background: white; padding: 20px; border-radius: 10px;">
                        <img src="data:image/png;base64,{b64}" style="width: 300px; height: 300px;" />
                    </div>
                </body>
                </html>
                """
                with open("qr_clean.html", "w") as f:
                    f.write(html_content)
                
                abs_path = os.path.abspath("qr_clean.html")
                print(f"Opening: {abs_path}")
                webbrowser.open(f"file://{abs_path}")
            else:
                print("❌ No base64/code in response.")
        else:
             print(f"❌ Error: {resp.status_code} | {resp.text}")

if __name__ == "__main__":
    asyncio.run(fetch_qr())
