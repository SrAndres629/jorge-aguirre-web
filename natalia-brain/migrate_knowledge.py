
import os
import sys

# Añadir el directorio raíz al path para importar app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import initialize, save_knowledge_fact
from app.config import settings

def migrate():
    print("🚀 Iniciando migración de conocimiento para Natalia...")
    
    if not initialize():
        print("❌ Error: No se pudo conectar a la base de datos.")
        return

    # Datos extraídos de core/app/services.py
    knowledge_data = [
        # SERVICIOS
        ("service_microblading_3d", "pricing", "Microblading de Cejas: Técnica pelo a pelo para un look natural 3D. Precio: $350."),
        ("service_delineado_ojos", "pricing", "Delineado Permanente: Realce de mirada con delineado superior e inferior. Precio: $300."),
        ("service_labios_full", "pricing", "Labios Full Color: Color completo y definición para labios perfectos. Precio: $400."),
        
        # NEGOCIO
        ("business_address", "location", "Dirección: Sobre el la av. 4to anillo y prolongacion av. brasil, frente al hospital guaracachi, Santa Cruz de la Sierra, Bolivia."),
        ("business_maps", "location", "Google Maps: https://maps.app.goo.gl/Nfqet1ArkDMMcPt76"),
        ("business_phone", "contact", "WhatsApp de contacto oficial: 59164714751"),
        
        # POLÍTICAS (De la lógica Senior)
        ("policy_preview", "policy", "Siempre preguntar a la clienta si tiene un trabajo previo (micropigmentación antigua) en la zona. Esto es vital para el diagnóstico."),
        ("policy_no_inventory", "policy", "No inventar ofertas si no están autorizadas por Jorge. Si hay dudas, Natalia consultará directamente con Jorge."),
    ]

    success_count = 0
    for slug, category, content in knowledge_data:
        if save_knowledge_fact(slug, category, content):
            success_count += 1
            print(f"✅ Conocimiento guardado: {slug}")
        else:
            print(f"❌ Error guardando: {slug}")

    print(f"\n✨ Migración terminada. {success_count}/{len(knowledge_data)} hechos cargados.")

if __name__ == "__main__":
    migrate()
