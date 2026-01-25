# =================================================================
# DATABASE.PY - Gestión Híbrida PostgreSQL / SQLite
# Jorge Aguirre Flores Web
# =================================================================
import logging
import sqlite3
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

from app.config import settings

# Intentar importar psycopg2 (PostgreSQL)
try:
    import psycopg2
    from psycopg2 import pool
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False

logger = logging.getLogger(__name__)

# Pool Global
_pg_pool: Optional[Any] = None

# Tipo de Backend Activo
BACKEND = "sqlite"  # 'postgres' o 'sqlite'

def init_pool() -> bool:
    """Inicializa la conexión a BD (Nube o Local)"""
    global _pg_pool, BACKEND
    
    # 1. Intentar PostgreSQL (Producción)
    if settings.DATABASE_URL and HAS_POSTGRES:
        try:
            _pg_pool = psycopg2.pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                dsn=settings.DATABASE_URL,
                # Senior Hardening: TCP Keepalives to prevent silent drops
                keepalives=1,
                keepalives_idle=30,
                keepalives_interval=10,
                keepalives_count=5
            )
            BACKEND = "postgres"
            logger.info("✅ Conexión PostgreSQL (Cloud) ESTABLECIDA")
            return True
        except Exception as e:
            logger.error(f"❌ Falló conexión PostgreSQL: {e}")
            import traceback
            logger.error(traceback.format_exc())
            # Fallback a SQLite
    
    # 2. Fallback a SQLite (Local)
    BACKEND = "sqlite"
    logger.info("⚠️ Usando SQLite (Local Fallback)")
    return True

@contextmanager
def get_cursor():
    """
    Obtiene un cursor con:
    1. Auto-Reconnect: Si la conexión está muerta, pide otra.
    2. Health Check: Ejecuta 'SELECT 1' antes de entregarla.
    3. Retry Logic: Reintenta hasta 3 veces si falla.
    """
    conn = None
    max_retries = 3
    is_postgres = (BACKEND == "postgres")
    
    last_error = None

    # RETRY LOOP
    for attempt in range(max_retries):
        try:
            if is_postgres:
                if _pg_pool is None:
                    if not init_pool():
                        raise Exception("Postgres Pool not initialized")

                # 1. Get Connection
                conn = _pg_pool.getconn()
                
                # 2. Health Check (Ping)
                is_healthy = False
                if conn.closed == 0:
                    try:
                        with conn.cursor() as test_cur:
                            test_cur.execute("SELECT 1")
                        is_healthy = True
                    except Exception:
                        pass # Ping failed
                
                if not is_healthy:
                    # Connection dead, discard and retry
                    logger.warning(f"⚠️ DB Connection dead (Attempt {attempt+1}/{max_retries}). Discarding...")
                    try:
                        _pg_pool.putconn(conn, close=True)
                    except: pass
                    conn = None
                    continue # Try next attempt (will get new conn from pool)

                # 3. Yield to Caller
                yield conn.cursor()
                conn.commit()
                return # Success!
                
            else:
                # SQLite Mode (Simple fallback)
                import os
                db_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database")
                os.makedirs(db_dir, exist_ok=True)
                db_path = os.path.join(db_dir, "local_fallback.db")
                conn = sqlite3.connect(db_path)
                yield SQLiteCursorWrapper(conn.cursor())
                conn.commit()
                return # Success

        except Exception as e:
            last_error = e
            logger.error(f"❌ Error DB (Attempt {attempt+1}/{max_retries}): {e}")
            if conn:
                try:
                    conn.rollback()
                except Exception: pass
                
                # Return/Close bad connection
                if is_postgres and _pg_pool:
                    try:
                        _pg_pool.putconn(conn, close=True) 
                    except: pass
                elif not is_postgres:
                    try:
                        conn.close()
                    except: pass
                conn = None
            
            # Don't sleep on last attempt
            if attempt < max_retries - 1:
                import time
                time.sleep(0.5)
    
    # If we got here, all retries failed
    logger.critical("🔥 CRITICAL: Database unreachable after retries.")
    raise last_error

class SQLiteCursorWrapper:
    """Adapta sintaxis Postgres (%s) a SQLite (?)"""
    def __init__(self, cursor):
        self.cursor = cursor
        
    def execute(self, sql, params=None):
        # Traducción simple de query params
        if params:
            # Reemplazar %s por ?
            sql = sql.replace("%s", "?")
            return self.cursor.execute(sql, params)
        return self.cursor.execute(sql)
        
    def fetchone(self):
        return self.cursor.fetchone()
        
    def fetchall(self):
        return self.cursor.fetchall()
        
    def close(self):
        self.cursor.close()

def init_tables():
    """Crea tablas si no existen, sincronizado con init_crm_master_clean.sql v2.0"""
    try:
        with get_cursor() as cur:
            if not cur: return False
            
            # --- Configuración de Tipos y Defaults ---
            if BACKEND == "postgres":
                id_type_uuid = "UUID PRIMARY KEY DEFAULT gen_random_uuid()"
                id_type_serial = "SERIAL PRIMARY KEY"
                timestamp_default = "CURRENT_TIMESTAMP"
                # Crear Enum en Postgres si no existe
                cur.execute("""
                    DO $$ BEGIN
                        CREATE TYPE lead_status AS ENUM (
                            'new', 'interested', 'nurturing', 'ghost', 'booked', 
                            'client_active', 'client_loyal', 'archived'
                        );
                    EXCEPTION WHEN duplicate_object THEN null; END $$;
                """)
                status_type = "lead_status DEFAULT 'new'"
            else:
                id_type_uuid = "TEXT PRIMARY KEY" # SQLite no tiene gen_random_uuid nativo
                id_type_serial = "INTEGER PRIMARY KEY AUTOINCREMENT"
                timestamp_default = "CURRENT_TIMESTAMP"
                status_type = "TEXT DEFAULT 'new'"

            # --- Tabla BUSINESS_KNOWLEDGE (Facts) ---
            sql_knowledge = f'''
                CREATE TABLE IF NOT EXISTS business_knowledge (
                    id {id_type_serial},
                    slug TEXT UNIQUE NOT NULL,
                    category TEXT NOT NULL, -- 'pricing', 'bio', 'location', 'policy'
                    content TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT {timestamp_default}
                );
            '''
            cur.execute(sql_knowledge)
            cur.execute('CREATE INDEX IF NOT EXISTS idx_knowledge_slug ON business_knowledge(slug);')

            # --- Tabla VISITORS (Anon Tracking) ---
            cur.execute(f'''
                CREATE TABLE IF NOT EXISTS visitors (
                    id {id_type_serial},
                    external_id TEXT,
                    fbclid TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    source TEXT,
                    utm_source TEXT,
                    utm_medium TEXT,
                    utm_campaign TEXT,
                    utm_term TEXT,
                    utm_content TEXT,
                    timestamp TIMESTAMP DEFAULT {timestamp_default}
                );
            ''')
            cur.execute('CREATE INDEX IF NOT EXISTS idx_visitors_external_id ON visitors(external_id);')

            # --- Tabla CONTACTS (CRM Master) ---
            # Nota: En SQLite usamos TEXT para UUID y manejamos la lógica en Python si es necesario
            sql_contacts = f'''
                CREATE TABLE IF NOT EXISTS contacts (
                    id {id_type_uuid if BACKEND == "postgres" else id_type_serial},
                    whatsapp_number TEXT UNIQUE NOT NULL,
                    full_name TEXT,
                    profile_pic_url TEXT,
                    
                    fb_click_id TEXT,
                    fb_browser_id TEXT,
                    utm_source TEXT,
                    utm_medium TEXT,
                    utm_campaign TEXT,
                    utm_term TEXT,
                    utm_content TEXT,
                    web_visit_count INTEGER DEFAULT 1,
                    conversion_sent_to_meta BOOLEAN DEFAULT FALSE,
                    
                    status {status_type},
                    lead_score INTEGER DEFAULT 50,
                    pain_point TEXT,
                    service_interest TEXT,
                    service_booked_date TIMESTAMP,
                    appointment_count INTEGER DEFAULT 0,
                    
                    created_at TIMESTAMP DEFAULT {timestamp_default},
                    updated_at TIMESTAMP,
                    last_interaction TIMESTAMP DEFAULT {timestamp_default}
                );
            '''
            cur.execute(sql_contacts)
            
            # --- Migración de Columnas (Si ya existe la tabla) ---
            new_columns = [
                ("profile_pic_url", "TEXT"),
                ("fb_browser_id", "TEXT"),
                ("utm_term", "TEXT"),
                ("utm_content", "TEXT"),
                ("status", status_type),
                ("lead_score", "INTEGER DEFAULT 50"),
                ("pain_point", "TEXT"),
                ("service_interest", "TEXT"),
                ("service_booked_date", "TIMESTAMP"),
                ("appointment_count", "INTEGER DEFAULT 0"),
                ("updated_at", "TIMESTAMP"),
                ("onboarding_step", "TEXT"), # Step de la entrevista (null, 'pricing', 'bio', etc)
                ("is_admin", "BOOLEAN DEFAULT FALSE")
            ]
            
            for col_name, col_type in new_columns:
                try:
                    if BACKEND == "postgres":
                        cur.execute(f"ALTER TABLE contacts ADD COLUMN IF NOT EXISTS {col_name} {col_type};")
                    else:
                        # SQLite no soporta IF NOT EXISTS en ALTER TABLE
                        # Debemos verificar si existe
                        cur.execute(f"PRAGMA table_info(contacts);")
                        cols = [c[1] for c in cur.fetchall()]
                        if col_name not in cols:
                            cur.execute(f"ALTER TABLE contacts ADD COLUMN {col_name} {col_type};")
                except Exception as e:
                    logger.warning(f"⚠️ Nota: Al intentar añadir {col_name}: {e}")

            cur.execute('CREATE INDEX IF NOT EXISTS idx_contacts_whatsapp ON contacts(whatsapp_number);')
            cur.execute('CREATE INDEX IF NOT EXISTS idx_contacts_status ON contacts(status);')

            # --- Tabla MESSAGES (AI Memory) ---
            # Forzado a INTEGER para contact_id para coincidir con SERIAL en contacts
            sql_messages = f'''
                CREATE TABLE IF NOT EXISTS messages (
                    id {id_type_uuid if BACKEND == "postgres" else id_type_serial},
                    contact_id INTEGER,
                    role TEXT CHECK (role IN ('user', 'assistant', 'system', 'tool')),
                    content TEXT,
                    created_at TIMESTAMP DEFAULT {timestamp_default},
                    FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE
                );
            '''
            cur.execute(sql_messages)
            cur.execute('CREATE INDEX IF NOT EXISTS idx_messages_contact_id ON messages(contact_id);')

            # --- Tabla APPOINTMENTS (Agendamiento) ---
            sql_appointments = f'''
                CREATE TABLE IF NOT EXISTS appointments (
                    id {id_type_serial},
                    contact_id INTEGER,
                    appointment_date TIMESTAMP NOT NULL,
                    service_type TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT {timestamp_default},
                    FOREIGN KEY (contact_id) REFERENCES contacts(id)
                );
            '''
            cur.execute(sql_appointments)
            
            # --- Tabla LEADS (W-003 Tracking Rescue) ---
            sql_leads = f'''
                CREATE TABLE IF NOT EXISTS leads (
                    id {id_type_uuid if BACKEND == "postgres" else id_type_serial}, -- Serial fallback for sqlite simple logic or text UUID
                    whatsapp_phone TEXT UNIQUE NOT NULL,
                    meta_lead_id TEXT,
                    click_id TEXT, -- fbclid
                    email TEXT,
                    name TEXT,
                    conversion_status TEXT DEFAULT 'NEW',
                    created_at TIMESTAMP DEFAULT {timestamp_default},
                    last_interaction TIMESTAMP DEFAULT {timestamp_default}
                );
            '''
            # Nota: Para SQLite usaremos Logic UUID en el insert si es necesario, pero aqui definimos Schema
            if BACKEND != "postgres":
                 # En SQLite preferimos TEXT para ID para consistencia con lógica de python uuid
                 sql_leads = sql_leads.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "TEXT PRIMARY KEY")

            cur.execute(sql_leads)
            cur.execute('CREATE INDEX IF NOT EXISTS idx_leads_phone ON leads(whatsapp_phone);')
            cur.execute('CREATE INDEX IF NOT EXISTS idx_leads_meta_id ON leads(meta_lead_id);')

            # --- Tabla INTERACTIONS (Contexto) ---
            sql_interactions = f'''
                CREATE TABLE IF NOT EXISTS interactions (
                    id {id_type_serial},
                    lead_id { 'UUID' if BACKEND == "postgres" else 'TEXT' },
                    role TEXT NOT NULL, -- 'user', 'system', 'assistant'
                    content TEXT,
                    timestamp TIMESTAMP DEFAULT {timestamp_default},
                    FOREIGN KEY (lead_id) REFERENCES leads(id) ON DELETE CASCADE
                );
            '''
            cur.execute(sql_interactions)
            cur.execute('CREATE INDEX IF NOT EXISTS idx_interactions_lead_id ON interactions(lead_id);')
            
        logger.info(f"✅ Tablas sincronizadas con Schema Natalia v2.0 ({BACKEND})")
        return True
    except Exception as e:
        logger.error(f"❌ Error sincronizando tablas: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

# =================================================================
# OPERATIONS
# =================================================================

def save_visitor(external_id, fbclid, ip_address, user_agent, source="pageview", utm_data=None):
    if utm_data is None:
        utm_data = {}
        
    with get_cursor() as cur:
        if cur:
            cur.execute(
                """
                INSERT INTO visitors (
                    external_id, fbclid, ip_address, user_agent, source,
                    utm_source, utm_medium, utm_campaign, utm_term, utm_content
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    external_id, 
                    fbclid, 
                    ip_address, 
                    user_agent[:500] if user_agent else None, 
                    source,
                    utm_data.get('utm_source'),
                    utm_data.get('utm_medium'),
                    utm_data.get('utm_campaign'),
                    utm_data.get('utm_term'),
                    utm_data.get('utm_content')
                )
            )

def upsert_contact_advanced(contact_data: Dict[str, Any]):
    """
    Upsert avanzado estilo CRM Natalia. Sincroniza marketing y ventas.
    """
    if BACKEND != "postgres":
        # Implementación parcial para SQLite para no romper dev
        with get_cursor() as cur:
            if cur:
                cur.execute("""
                    INSERT INTO contacts (whatsapp_number, full_name, utm_source, status)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT(whatsapp_number) DO UPDATE SET
                        full_name = EXCLUDED.full_name,
                        utm_source = COALESCE(EXCLUDED.utm_source, contacts.utm_source),
                        last_interaction = CURRENT_TIMESTAMP
                """, (
                    contact_data.get('phone'), 
                    contact_data.get('name'), 
                    contact_data.get('utm_source'),
                    contact_data.get('status', 'new')
                ))
        return

    sql = """
    INSERT INTO contacts (
        whatsapp_number, full_name, profile_pic_url,
        fb_click_id, fb_browser_id,
        utm_source, utm_medium, utm_campaign, utm_term, utm_content,
        status, lead_score, pain_point, service_interest,
        last_interaction
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
    ON CONFLICT (whatsapp_number) 
    DO UPDATE SET 
        full_name = COALESCE(EXCLUDED.full_name, contacts.full_name),
        profile_pic_url = COALESCE(EXCLUDED.profile_pic_url, contacts.profile_pic_url),
        fb_click_id = COALESCE(EXCLUDED.fb_click_id, contacts.fb_click_id),
        utm_source = COALESCE(EXCLUDED.utm_source, contacts.utm_source),
        status = COALESCE(EXCLUDED.status, contacts.status),
        lead_score = COALESCE(EXCLUDED.lead_score, contacts.lead_score),
        pain_point = COALESCE(EXCLUDED.pain_point, contacts.pain_point),
        service_interest = COALESCE(EXCLUDED.service_interest, contacts.service_interest),
        last_interaction = NOW(),
        web_visit_count = contacts.web_visit_count + 1,
        updated_at = NOW();
    """
    
    params = (
        contact_data.get('phone'),
        contact_data.get('name'),
        contact_data.get('profile_pic_url'),
        contact_data.get('fbclid'),
        contact_data.get('fbp'),
        contact_data.get('utm_source'),
        contact_data.get('utm_medium'),
        contact_data.get('utm_campaign'),
        contact_data.get('utm_term'),
        contact_data.get('utm_content'),
        contact_data.get('status', 'new'),
        contact_data.get('lead_score', 50),
        contact_data.get('pain_point'),
        contact_data.get('service_interest')
    )

    try:
        with get_cursor() as cur:
            if cur:
                cur.execute(sql, params)
                logger.info(f"🚀 Natalia Sync Success: {contact_data.get('phone')}")
    except Exception as e:
        logger.error(f"❌ Natalia Sync Error: {e}")

# Backward compatibility alias
upsert_contact = upsert_contact_advanced

def save_message(whatsapp_number: str, role: str, content: str):
    """Guarda un mensaje en el historial para memoria de Natalia"""
    try:
        with get_cursor() as cur:
            if not cur: return
            
            # 1. Obtener contact_id
            cur.execute("SELECT id FROM contacts WHERE whatsapp_number = %s", (whatsapp_number,))
            row = cur.fetchone()
            if not row:
                # Si no existe, lo creamos mínimo
                upsert_contact_advanced({'phone': whatsapp_number, 'status': 'new'})
                cur.execute("SELECT id FROM contacts WHERE whatsapp_number = %s", (whatsapp_number,))
                row = cur.fetchone()
            
            contact_id = row[0]
            
            # 2. Insertar mensaje
            if BACKEND == "postgres":
                sql = "INSERT INTO messages (contact_id, role, content) VALUES (%s, %s, %s)"
            else:
                sql = "INSERT INTO messages (contact_id, role, content) VALUES (%s, %s, %s)"
                
            cur.execute(sql, (contact_id, role, content))
    except Exception as e:
        logger.error(f"❌ Error guardando mensaje: {e}")

def get_chat_history(whatsapp_number: str, limit: int = 10):
    """Obtiene los últimos N mensajes para contexto de la IA"""
    history = []
    try:
        with get_cursor() as cur:
            if not cur: return []
            cur.execute("""
                SELECT m.role, m.content 
                FROM messages m
                JOIN contacts c ON m.contact_id = c.id
                WHERE c.whatsapp_number = %s
                ORDER BY m.created_at DESC
                LIMIT %s
            """, (whatsapp_number, limit))
            rows = cur.fetchall()
            # Invertir para que sea cronológico
            for row in reversed(rows):
                history.append({"role": row[0], "content": row[1]})
    except Exception as e:
        logger.error(f"❌ Error obteniendo historial: {e}")
    return history


def get_visitor_fbclid(external_id):
    with get_cursor() as cur:
        if cur:
            cur.execute(
                "SELECT fbclid FROM visitors WHERE external_id = %s AND fbclid IS NOT NULL ORDER BY timestamp DESC LIMIT 1",
                (external_id,)
            )
            row = cur.fetchone()
            return row[0] if row else None
    return None

def initialize():
    if init_pool():
        init_tables()
        return True
    return False

def get_all_visitors(limit: int = 50) -> List[Dict[str, Any]]:
    """Obtiene los últimos visitantes para el dashboard"""
    visitors = []
    try:
        with get_cursor() as cur:
            if cur:
                cur.execute(
                    "SELECT id, external_id, source, timestamp, ip_address FROM visitors ORDER BY timestamp DESC LIMIT %s",
                    (limit,)
                )
                rows = cur.fetchall()
                for row in rows:
                    visitors.append({
                        "id": row[0],
                        "external_id": row[1],
                        "source": row[2],
                        "timestamp": row[3],
                        "ip_address": row[4]
                    })
    except Exception as e:
        logger.error(f"❌ Error obteniendo visitors: {e}")
    return visitors

def get_visitor_by_id(visitor_id: int) -> Optional[Dict[str, Any]]:
    """Obtiene un visitante por ID"""
    try:
        with get_cursor() as cur:
            if cur:
                cur.execute(
                    "SELECT id, external_id, fbclid, source, timestamp FROM visitors WHERE id = %s",
                    (visitor_id,)
                )
                row = cur.fetchone()
                if row:
                    return {
                        "id": row[0],
                        "external_id": row[1],
                        "fbclid": row[2],
                        "source": row[3],
                        "timestamp": row[4]
                    }
    except Exception as e:
        logger.error(f"❌ Error buscando visitor {visitor_id}: {e}")
    return None



# =================================================================
# W-003 TRACKING OPERATIONS (Tracking Rescue)
# =================================================================

def mark_lead_sent(whatsapp_number: str) -> bool:
    """Marca a un usuario como ya enviado a Meta para evitar duplicados (Senior Guard)"""
    try:
        with get_cursor() as cur:
            if not cur: return False
            cur.execute(
                "UPDATE contacts SET conversion_sent_to_meta = TRUE WHERE whatsapp_number = %s",
                (whatsapp_number,)
            )
            return True
    except Exception as e:
        logger.error(f"❌ Error marcando lead enviado: {e}")
        return False

def get_user_message_count(whatsapp_number: str) -> int:
    """Cuenta cuántos mensajes ha enviado el USUARIO para el filtro de calidad"""
    try:
        with get_cursor() as cur:
            if not cur: return 0
            # Solo contamos mensajes con role 'user'
            cur.execute("""
                SELECT COUNT(*) FROM messages m
                JOIN contacts c ON m.contact_id = c.id
                WHERE c.whatsapp_number = %s AND m.role = 'user'
            """, (whatsapp_number,))
            row = cur.fetchone()
            return row[0] if row else 0
    except Exception as e:
        logger.error(f"❌ Error contando mensajes: {e}")
        return 0

def check_if_lead_sent(whatsapp_number: str) -> bool:
    """Verifica si ya pagamos a Meta por este Lead (Financial Shield)"""
    try:
        with get_cursor() as cur:
            if not cur: return False
            cur.execute(
                "SELECT conversion_sent_to_meta FROM contacts WHERE whatsapp_number = %s",
                (whatsapp_number,)
            )
            row = cur.fetchone()
            return row[0] if row else False
    except Exception as e:
        logger.error(f"❌ Error verificando lead enviado: {e}")
        return False

def get_meta_data_by_ref(ref_tag: str) -> Optional[Dict[str, Any]]:
    """Recupera cookies fbc/fbp usando el [Ref Tag] del mensaje de WA"""
    try:
        with get_cursor() as cur:
            if not cur: return None
            # Buscamos en visitantes el external_id que empiece con el tag (8 chars)
            cur.execute("""
                SELECT fbclid, user_agent, ip_address, utm_source, utm_medium, utm_campaign
                FROM visitors 
                WHERE external_id LIKE %s 
                ORDER BY timestamp DESC LIMIT 1
            """, (f"{ref_tag}%",))
            row = cur.fetchone()
            if row:
                return {
                    "fbclid": row[0],
                    "user_agent": row[1],
                    "ip_address": row[2],
                    "utm_source": row[3],
                    "utm_medium": row[4],
                    "utm_campaign": row[5]
                }
    except Exception as e:
        logger.error(f"❌ Error buscando meta data por ref: {e}")
    return None

def get_or_create_lead(whatsapp_phone: str, meta_data: Optional[dict] = None) -> Optional[str]:
    """
    Obtiene o crea un Lead basado en el teléfono.
    Vincula datos de Meta (Click ID, Lead ID) si se proveen.
    Retorna el ID del Lead (UUID string o int string).
    """
    if meta_data is None:
        meta_data = {}

    try:
        with get_cursor() as cur:
            if not cur: return None

            # 1. Buscar Lead existente
            cur.execute("SELECT id FROM leads WHERE whatsapp_phone = %s", (whatsapp_phone,))
            row = cur.fetchone()

            if row:
                lead_id = row[0]
                # Update si hay nuevos datos de Meta
                if meta_data:
                    sql_update = """
                        UPDATE leads SET 
                            meta_lead_id = COALESCE(%s, meta_lead_id),
                            click_id = COALESCE(%s, click_id),
                            email = COALESCE(%s, email),
                            name = COALESCE(%s, name),
                            last_interaction = CURRENT_TIMESTAMP
                        WHERE id = %s
                    """
                    cur.execute(sql_update, (
                        meta_data.get('meta_lead_id'),
                        meta_data.get('click_id'),
                        meta_data.get('email'),
                        meta_data.get('name'),
                        lead_id
                    ))
                return str(lead_id)

            # 2. Crear Nuevo Lead
            logger.info(f"✨ Creando Nuevo Lead: {whatsapp_phone}")
            if BACKEND == "postgres":
                sql_insert = """
                    INSERT INTO leads (whatsapp_phone, meta_lead_id, click_id, email, name)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """
                cur.execute(sql_insert, (
                    whatsapp_phone,
                    meta_data.get('meta_lead_id'),
                    meta_data.get('click_id'),
                    meta_data.get('email'),
                    meta_data.get('name')
                ))
                lead_id = cur.fetchone()[0]
                return str(lead_id)
            else:
                # SQLite Logic
                import uuid
                new_id = str(uuid.uuid4())
                sql_insert = """
                    INSERT INTO leads (id, whatsapp_phone, meta_lead_id, click_id, email, name)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cur.execute(sql_insert, (
                    new_id,
                    whatsapp_phone,
                    meta_data.get('meta_lead_id'),
                    meta_data.get('click_id'),
                    meta_data.get('email'),
                    meta_data.get('name')
                ))
                return new_id

    except Exception as e:
        logger.error(f"❌ Error en get_or_create_lead: {e}")
        return None

def log_interaction(lead_id: str, role: str, content: str) -> bool:
    """Registra una interacción (mensaje) para el Lead"""
    try:
        with get_cursor() as cur:
            if not cur: return False
            
            if BACKEND == "postgres":
                 # Postgres casteo automático si definimos UUID en tabla
                sql = "INSERT INTO interactions (lead_id, role, content) VALUES (%s, %s, %s)"
            else:
                sql = "INSERT INTO interactions (lead_id, role, content) VALUES (%s, %s, %s)"

            cur.execute(sql, (lead_id, role, content))
            return True
    except Exception as e:
        logger.error(f"❌ Error en log_interaction: {e}")
        return False


# =================================================================
# NATALIA KNOWLEDGE BASE
# =================================================================

def save_knowledge_fact(slug: str, category: str, content: str):
    """Guarda o actualiza un hecho en la base de conocimiento"""
    try:
        with get_cursor() as cur:
            if not cur: return False
            
            if BACKEND == "postgres":
                sql = """
                    INSERT INTO business_knowledge (slug, category, content, updated_at)
                    VALUES (%s, %s, %s, NOW())
                    ON CONFLICT (slug) DO UPDATE SET
                        content = EXCLUDED.content,
                        category = EXCLUDED.category,
                        updated_at = NOW();
                """
            else:
                sql = """
                    INSERT INTO business_knowledge (slug, category, content)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (slug) DO UPDATE SET
                        content = EXCLUDED.content,
                        category = EXCLUDED.category;
                """
            cur.execute(sql, (slug, category, content))
            logger.info(f"🧠 Natalia Learned: {slug} ({category})")
            return True
    except Exception as e:
        logger.error(f"❌ Error guardando conocimiento: {e}")
        return False

def get_knowledge_base(category: Optional[str] = None) -> List[Dict[str, Any]]:
    """Obtiene el conocimiento del negocio, opcionalmente por categoría"""
    facts = []
    try:
        with get_cursor() as cur:
            if not cur: return []
            
            if category:
                sql = "SELECT slug, category, content FROM business_knowledge WHERE category = %s"
                params = (category,)
            else:
                sql = "SELECT slug, category, content FROM business_knowledge"
                params = None
                
            cur.execute(sql, params)
            rows = cur.fetchall()
            for row in rows:
                facts.append({"slug": row[0], "category": row[1], "content": row[2]})
    except Exception as e:
        logger.error(f"❌ Error obteniendo conocimiento: {e}")
    return facts

def get_knowledge_value(slug: str) -> Optional[str]:
    """Obtiene un valor específico del conocimiento"""
    try:
        with get_cursor() as cur:
            if not cur: return None
            cur.execute("SELECT content FROM business_knowledge WHERE slug = %s", (slug,))
            row = cur.fetchone()
            return row[0] if row else None
    except Exception as e:
        logger.error(f"❌ Error obteniendo valor de conocimiento: {e}")
    return None

def check_connection() -> bool:
    """Verifica si hay conexión a BD"""
    try:
        with get_cursor() as cur:
            if cur:
                cur.execute("SELECT 1")
                return True
    except Exception:
        pass
    return False

