# =================================================================
# DATABASE.PY - Gestión de PostgreSQL (Supabase)
# Jorge Aguirre Flores Web
# =================================================================
import psycopg2
from psycopg2 import pool
from contextlib import contextmanager
from typing import Optional, List, Dict, Any
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# Connection Pool (reutilización de conexiones)
_connection_pool: Optional[pool.SimpleConnectionPool] = None


def init_pool():
    """Inicializa el pool de conexiones"""
    global _connection_pool
    
    if not settings.DATABASE_URL:
        logger.info("ℹ️ DATABASE_URL no configurado - Pool no inicializado")
        return False
    
    try:
        _connection_pool = pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            dsn=settings.DATABASE_URL
        )
        logger.info("✅ Pool de conexiones PostgreSQL inicializado")
        return True
    except Exception as e:
        logger.error(f"❌ Error inicializando pool: {e}")
        return False


@contextmanager
def get_cursor():
    """Context manager para obtener cursor de forma segura"""
    if not _connection_pool:
        yield None
        return
    
    conn = None
    try:
        conn = _connection_pool.getconn()
        cursor = conn.cursor()
        yield cursor
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"❌ Error en operación DB: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            _connection_pool.putconn(conn)


def init_tables():
    """Inicializa las tablas necesarias"""
    if not _connection_pool:
        logger.warning("⚠️ Sin conexión a DB - saltando init_tables")
        return False
    
    try:
        with get_cursor() as cur:
            if cur is None:
                return False
            
            # Tabla de visitantes
            cur.execute('''
                CREATE TABLE IF NOT EXISTS visitors (
                    id SERIAL PRIMARY KEY,
                    external_id TEXT NOT NULL,
                    fbclid TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    source TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            ''')
            
            # Índices para búsquedas rápidas
            cur.execute('CREATE INDEX IF NOT EXISTS idx_visitors_external_id ON visitors(external_id);')
            cur.execute('CREATE INDEX IF NOT EXISTS idx_visitors_fbclid ON visitors(fbclid);')
            
        logger.info("✅ Tablas PostgreSQL inicializadas")
        return True
    except Exception as e:
        logger.error(f"❌ Error init_tables: {e}")
        return False


# =================================================================
# CRUD OPERATIONS
# =================================================================

def save_visitor(
    external_id: str, 
    fbclid: Optional[str], 
    ip_address: str, 
    user_agent: Optional[str], 
    source: str = "pageview"
) -> bool:
    """Guarda un registro de visitante"""
    try:
        with get_cursor() as cur:
            if cur is None:
                return False
            
            cur.execute(
                """INSERT INTO visitors 
                   (external_id, fbclid, ip_address, user_agent, source) 
                   VALUES (%s, %s, %s, %s, %s)""",
                (
                    external_id, 
                    fbclid, 
                    ip_address, 
                    user_agent[:500] if user_agent else None, 
                    source
                )
            )
        logger.info(f"[DB] Visitor saved: fbclid={bool(fbclid)}, source={source}")
        return True
    except Exception as e:
        logger.error(f"❌ Error save_visitor: {e}")
        return False


def get_visitor_fbclid(external_id: str) -> Optional[str]:
    """Recupera el fbclid de un visitante por su external_id"""
    try:
        with get_cursor() as cur:
            if cur is None:
                return None
            
            cur.execute(
                """SELECT fbclid FROM visitors 
                   WHERE external_id = %s AND fbclid IS NOT NULL 
                   ORDER BY timestamp DESC LIMIT 1""",
                (external_id,)
            )
            row = cur.fetchone()
            return row[0] if row else None
    except Exception as e:
        logger.error(f"❌ Error get_visitor_fbclid: {e}")
        return None


def get_all_visitors(limit: int = 50) -> List[Dict[str, Any]]:
    """Obtiene los últimos N visitantes"""
    try:
        with get_cursor() as cur:
            if cur is None:
                return []
            
            cur.execute("""
                SELECT id, external_id, fbclid, ip_address, user_agent, source, timestamp::text 
                FROM visitors ORDER BY timestamp DESC LIMIT %s
            """, (limit,))
            
            rows = cur.fetchall()
            return [
                {
                    "id": r[0],
                    "external_id": r[1],
                    "fbclid": r[2],
                    "ip_address": r[3],
                    "user_agent": r[4],
                    "source": r[5],
                    "timestamp": r[6]
                }
                for r in rows
            ]
    except Exception as e:
        logger.error(f"❌ Error get_all_visitors: {e}")
        return []


def get_visitor_by_id(visitor_id: int) -> Optional[Dict[str, Any]]:
    """Obtiene un visitante por ID"""
    try:
        with get_cursor() as cur:
            if cur is None:
                return None
            
            cur.execute(
                "SELECT id, external_id, fbclid FROM visitors WHERE id = %s", 
                (visitor_id,)
            )
            row = cur.fetchone()
            
            if row:
                return {"id": row[0], "external_id": row[1], "fbclid": row[2]}
            return None
    except Exception as e:
        logger.error(f"❌ Error get_visitor_by_id: {e}")
        return None


def check_connection() -> bool:
    """Verifica si la conexión a DB está activa"""
    if not _connection_pool:
        return False
    
    try:
        with get_cursor() as cur:
            if cur:
                cur.execute("SELECT 1")
                return True
        return False
    except Exception:
        return False


# =================================================================
# INICIALIZACIÓN
# =================================================================

def initialize():
    """Inicializa la base de datos completa"""
    if init_pool():
        init_tables()
        return True
    return False
