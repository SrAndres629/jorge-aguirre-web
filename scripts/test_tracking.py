
import sys
import os
import asyncio
from datetime import datetime

# Add core path
sys.path.append(os.path.join(os.getcwd(), 'core'))

from app.database import initialize, get_or_create_lead, log_interaction
from app.models import LeadCreate

def test_tracking_flow():
    print("🚀 Iniciando Test de Rastreo (W-003)...")
    
    # 1. Initialize DB
    if not initialize():
        print("❌ Falló inicialización de DB")
        return

    # 2. Mock Data (Simulating incoming webhook from n8n)
    mock_phone = "59160000000"
    mock_meta_data = {
        "meta_lead_id": "lead_123456789",
        "click_id": "fbclid_test_xyz",
        "email": "test@example.com",
        "name": "Test User"
    }

    print(f"📡 Simulando Lead: {mock_phone}")

    # 3. Create/Get Lead
    lead_id = get_or_create_lead(mock_phone, mock_meta_data)
    
    if lead_id:
        print(f"✅ Lead obtenido/creado ID: {lead_id}")
    else:
        print("❌ Falló creación de Lead")
        return

    # 4. Log Interaction
    msg = "Hola, vi el anuncio de microblading."
    print(f"💬 Guardando interacción: '{msg}'")
    success = log_interaction(lead_id, "user", msg)
    
    if success:
        print("✅ Interacción guardada")
    else:
        print("❌ Falló guardado de interacción")

if __name__ == "__main__":
    test_tracking_flow()
