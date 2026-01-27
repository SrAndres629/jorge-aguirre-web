import asyncio
import sys
import os
import base64

# Add current directory to path
sys.path.append(os.getcwd())

from app.evolution import evolution_service
from app.config import settings

async def main():
    print(f"🔧 Configuring Evolution API Instance: {settings.EVOLUTION_INSTANCE}")
    print(f"Target: {settings.EVOLUTION_API_URL}")

    # 1. Check Status
    print("Checking status...")
    status = await evolution_service.get_instance_status()
    print(f"Current Status: {status}")

    # 2. Create if not exists
    # If 404 or "Instance not found"
    if isinstance(status, dict) and (status.get("message") == "Instance not found" or status.get("status") == 404):
        print("🚀 Instance not found. Creating 'JorgeMain'...")
        created = await evolution_service.create_instance()
        if not created:
             print("❌ Failed to create instance. Check logs.")
             return
        print("✅ Instance created.")
        # Wait a bit for it to spin up
        await asyncio.sleep(2)

    # 3. Get QR
    print("📡 Fetching QR Code for authentication...")
    qr_base64 = await evolution_service.connect_instance()
    
    if qr_base64:
        print("✅ QR Code received!")
        # Clean base64 string
        if 'base64,' in qr_base64:
            qr_base64 = qr_base64.split('base64,')[1]
            
        img_data = base64.b64decode(qr_base64)
        
        # Save to root for easy access
        output_file = "whatsapp_qr.png"
        with open(output_file, "wb") as f:
            f.write(img_data)
            
        print(f"💾 QR Code saved to: {os.path.abspath(output_file)}")
        print("👉 ACTION REQUIRED: Open this image and scan it with WhatsApp!")
    else:
        print("ℹ️ No QR Code returned. Possibilities:")
        print("1. Instance is already connected (Good!)")
        print("2. Evolution API is still initializing.")

if __name__ == "__main__":
    asyncio.run(main())
