import os
import logging
import psycopg2
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

def fix_security():
    if not DATABASE_URL:
        logger.error("❌ No se encontró DATABASE_URL en el archivo .env")
        return

    try:
        logger.info("🔌 Conectando a Supabase PostgreSQL...")
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        # 1. Habilitar RLS en la tabla visitors
        logger.info("🛡️ Habilitando Row Level Security (RLS) en 'visitors'...")
        cur.execute("ALTER TABLE IF EXISTS public.visitors ENABLE ROW LEVEL SECURITY;")
        
        # 2. Crear política para permitir acceso total al rol 'postgres' y 'service_role' (por defecto tienen bypass, pero esto es explícito)
        # En realidad, al habilitar RLS, el dueño (postgres) sigue teniendo acceso.
        # Bloqueamos el acceso "anon" (público) implícitamente al no crear políticas para él.
        
        conn.commit()
        cur.close()
        conn.close()
        logger.info("✅ ¡Seguridad aplicada correctamente! La advertencia en Supabase debería desaparecer.")
        logger.info("ℹ️ Nota: Tu aplicación Python seguirá funcionando porque se conecta como administrador.")

    except Exception as e:
        logger.error(f"❌ Error aplicando seguridad: {e}")

if __name__ == "__main__":
    fix_security()
