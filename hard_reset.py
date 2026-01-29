import httpx
import asyncio
import json
import webbrowser
import os
import base64

API_URL = "https://evolution-whatsapp-zn13.onrender.com"
API_KEY = "JorgeSecureKey123"
INSTANCE = "NataliaBrain"

async def hard_reset():
    headers = {"apikey": API_KEY, "Content-Type": "application/json"}
    print(f"💀 INITIATING HARD RESET FOR: {INSTANCE}")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. LOGOUT (Try to clean session on WA side)
        print("   🔌 Logging out...")
        try:
            await client.delete(f"{API_URL}/instance/logout/{INSTANCE}", headers=headers)
        except:
            pass

        # 2. DELETE (Clear DB)
        print("   🗑️  Deleting Instance...")
        try:
            resp = await client.delete(f"{API_URL}/instance/delete/{INSTANCE}", headers=headers)
            print(f"      Result: {resp.status_code}")
        except Exception as e:
            print(f"      Error: {e}")

        # 3. WAIT (Let DB settle)
        print("   ⏳ Waiting 5s for cleanup...")
        await asyncio.sleep(5)

        # 4. CREATE
        print(f"   ✨ Creating Fresh Instance: {INSTANCE}")
        body = {
            "instanceName": INSTANCE,
            "token": API_KEY,
            "qrcode": True
        }
        resp = await client.post(f"{API_URL}/instance/create", json=body, headers=headers)
        print(f"      Create: {resp.status_code}")

        # 5. GET QR
        print("   📸 Fetching New QR Code...")
        resp = await client.get(f"{API_URL}/instance/connect/{INSTANCE}", headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            # Evolution returns base64 or code depending on version.
            # Usually {"base64": "..."} or {"code": "..."}
            
            b64 = data.get("base64") or data.get("code") # Try both
            
            if b64:
                # Clean up b64 if needed
                if b64.startswith("data:image"):
                    b64 = b64.split(",")[1]
                
                # Verify length
                if len(b64) < 100:
                     print(f"      ⚠️ Invalid QR Data: {data}")
                     return

                # Save
                html_content = f"""
                <html>
                <body style="background-color: #1a1a1a; display: flex; justify-content: center; align-items: center; height: 100vh; flex-direction: column; color: white; font-family: sans-serif;">
                    <h1>🤖 Natalia Brain Hard Reset</h1>
                    <p>Scan this QR Code IMMEDIATELY.</p>
                    <div style="background: white; padding: 20px; border-radius: 10px;">
                        <img src="data:image/png;base64,{b64}" style="width: 300px; height: 300px;" />
                    </div>
                </body>
                </html>
                """
                
                with open("qr_hard_reset.html", "w") as f:
                    f.write(html_content)
                
                print("\n✅ QR CODE GENERATED: qr_hard_reset.html")
                abs_path = os.path.abspath("qr_hard_reset.html")
                webbrowser.open(f"file://{abs_path}")
            else:
                print("      ❌ No QR data found in response.")
        else:
             print(f"      ❌ Failed to fetch connect data: {resp.status_code}")

if __name__ == "__main__":
    asyncio.run(hard_reset())
