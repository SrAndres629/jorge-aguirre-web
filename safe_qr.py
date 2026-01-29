import httpx
import asyncio
import webbrowser
import os
import json

API_URL = "https://evolution-whatsapp-zn13.onrender.com"
API_KEY = "JorgeSecureKey123"
INSTANCE = "NataliaBrain"

async def safe_fetch_qr():
    headers = {"apikey": API_KEY, "Content-Type": "application/json"}
    print(f"FETCHING QR FOR: {INSTANCE}")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(f"{API_URL}/instance/connect/{INSTANCE}", headers=headers)
            
            if resp.status_code == 200:
                data = resp.json()
                b64 = data.get("base64") or data.get("code")
                
                if b64:
                    if b64.startswith("data:image"):
                        b64 = b64.split(",")[1]
                    
                    print(f"QR Data Recieved. Length: {len(b64)}")
                    
                    html_content = f"""
                    <html>
                    <body style="background-color: #1a1a1a; display: flex; justify-content: center; align-items: center; height: 100vh; flex-direction: column; color: white; font-family: sans-serif;">
                        <h1>🤖 Natalia Brain (Safe Mode)</h1>
                        <p>Status: {data.get('instance', {}).get('state')}</p>
                        <p>Scan this QR Code to Link.</p>
                        <div style="background: white; padding: 20px; border-radius: 10px;">
                            <img src="data:image/png;base64,{b64}" style="width: 300px; height: 300px;" />
                        </div>
                    </body>
                    </html>
                    """
                    filename = "qr_safe.html"
                    # Force utf-8 writing
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(html_content)
                    
                    abs_path = os.path.abspath(filename)
                    # DO NOT print the path if it might contain non-ascii characters
                    print("QR HTML File Created: qr_safe.html") 
                    
                    try:
                        # webbrowser might fail if path has crazy chars, but let's try
                        webbrowser.open(f"file://{abs_path}")
                        print("Browser opened.")
                    except Exception as e:
                        print(f"Browser launch error: {e}")
                        print("Please open qr_safe.html manually.")
                else:
                    print("No base64/code in response.")
            else:
                 print(f"Error: {resp.status_code}")
                 # Print only safe ascii of response text
                 print(f"Response: {resp.text.encode('ascii', 'ignore').decode('ascii')}")
        except Exception as e:
            print(f"Request Error: {e}")

if __name__ == "__main__":
    asyncio.run(safe_fetch_qr())
