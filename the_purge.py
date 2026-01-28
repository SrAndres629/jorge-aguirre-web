import httpx
import asyncio
import os
import sys
import webbrowser

# Configuration - MASTER KEYS
API_URL = "https://evolution-whatsapp-zn13.onrender.com"
API_KEY = "JorgeSecureKey123"
NEW_INSTANCE = "NataliaBrain"
WEBHOOK_URL = "https://natalia-brain.onrender.com/webhook/evolution"

async def the_purge():
    print("⚔️  INITIATING PROTOCOL: THE PURGE")
    print(f"Target API: {API_URL}")
    
    headers = {
        "apikey": API_KEY,
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # STEP 1: DELETE OLD INSTANCES
        targets = ["NataliaCoreV1", "NataliaCoreProd"]
        print("\n🗑️  PHASE 1: CLEANUP")
        for target in targets:
            print(f"   -> Terminating {target}...")
            # Logout first (failsafe)
            try:
                await client.delete(f"{API_URL}/instance/logout/{target}", headers=headers)
            except: pass
            
            # Delete
            try:
                resp = await client.delete(f"{API_URL}/instance/delete/{target}", headers=headers)
                print(f"      Status: {resp.status_code}")
            except Exception as e:
                print(f"      Error: {e}")

        # STEP 2: CREATE NATALIA BRAIN
        print(f"\n✨ PHASE 2: FORGING {NEW_INSTANCE}")
        payload = {
            "instanceName": NEW_INSTANCE,
            "token": API_KEY, # Using Master Key as token for simplicity
            "qrcode": True,
            "integration": "WHATSAPP-BAILEYS"
        }
        try:
            resp = await client.post(f"{API_URL}/instance/create", json=payload, headers=headers)
            print(f"   Status: {resp.status_code} | {resp.text}")
            if resp.status_code not in [200, 201] and "already in use" not in resp.text:
                print("   ❌ CRITICAL FAILURE IN CREATION")
                return
        except Exception as e:
            print(f"   ❌ Network Error: {e}")
            return

        # STEP 3: FETCH QR
        print("\n🔗 PHASE 3: CONNECTION LINK")
        try:
            resp = await client.get(f"{API_URL}/instance/connect/{NEW_INSTANCE}", headers=headers)
            data = resp.json()
            
            qr_base64 = None
            if "base64" in data: qr_base64 = data["base64"]
            elif "qrcode" in data and "base64" in data["qrcode"]: qr_base64 = data["qrcode"]["base64"]
            
            if qr_base64:
                html = f"""<html><body style='background-color:#111;color:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;height:100vh;font-family:sans-serif'>
                <h1>💀 THE PURGE COMPLETE</h1>
                <h2>Scan to Activate: {NEW_INSTANCE}</h2>
                <img src='{qr_base64}' style='border:10px solid #fff;border-radius:10px'/>
                </body></html>"""
                
                with open("qr_natalia.html", "w", encoding="utf-8") as f: f.write(html)
                print("   ✅ QR Generated: qr_natalia.html")
                webbrowser.open("qr_natalia.html")
            else:
                print("   ⚠️ No QR Code returned (Already Connected?)")
                
        except Exception as e:
            print(f"   ❌ Fetch Error: {e}")

        # STEP 4: SET WEBHOOK
        print("\n👂 PHASE 4: CONNECTING EARS (WEBHOOK)")
        webhook_payload = {
            "webhook": {
                "enabled": True,
                "url": WEBHOOK_URL,
                "webhookByEvents": True,
                "events": ["MESSAGES_UPSERT", "MESSAGES_UPDATE", "SEND_MESSAGE", "CONNECTION_UPDATE"]
            }
        }
        try:
            resp = await client.post(f"{API_URL}/webhook/set/{NEW_INSTANCE}", json=webhook_payload, headers=headers)
            print(f"   Status: {resp.status_code} | {resp.text}")
        except Exception as e:
            print(f"   ❌ Webhook Error: {e}")

    print("\n🏁 PURGE PROTOCOL COMPLETE.")

if __name__ == "__main__":
    asyncio.run(the_purge())
