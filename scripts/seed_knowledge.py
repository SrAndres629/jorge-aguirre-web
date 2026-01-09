
import sys
import os
import logging

# Add core to path
sys.path.append(os.path.join(os.getcwd(), 'core'))

from app import database
from app.database import save_knowledge_fact

# Config logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SeedKnowledge")

KNOWLEDGE = [
    {
        "slug": "pricing_microblading",
        "category": "pricing",
        "content": "El servicio de Microblading tiene un costo base de $150 USD. Incluye diseño, anestesia tópica y procedimiento."
    },
    {
        "slug": "pricing_lips",
        "category": "pricing",
        "content": "Full Lips (Labios) cuesta $200 USD. Incluye neutralización de color si es necesario."
    },
    {
        "slug": "location_main",
        "category": "location",
        "content": "Estamos ubicados en Zona Equipetrol, Calle Tucumán #45, Edificio Design Center, Piso 2, Consultorio 204."
    },
    {
        "slug": "welcome_video",
        "category": "media",
        "content": "https://jorgeaguirreflores.com/static/videos/welcome.mp4"
    }
]

def seed():
    logger.info("🌱 Seeding Natalia Knowledge Base...")
    
    # Initialize DB (Postgres or SQLite)
    if not database.initialize():
        logger.error("❌ Failed to connect to DB")
        return

    for item in KNOWLEDGE:
        success = save_knowledge_fact(item['slug'], item['category'], item['content'])
        if success:
            logger.info(f"✅ Saved: {item['slug']}")
        else:
            logger.warning(f"⚠️ Failed: {item['slug']}")

if __name__ == "__main__":
    seed()
