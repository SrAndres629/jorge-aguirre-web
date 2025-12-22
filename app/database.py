# =================================================================
# DATABASE.PY - Gestión Híbrida PostgreSQL / SQLite
# Jorge Aguirre Flores Web
# =================================================================
import os
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
                dsn=settings.DATABASE_URL
            )
            BACKEND = "postgres"
            logger.info("✅ Conexión PostgreSQL (Cloud) ESTABLECIDA")
            return True
        except Exception as e:
            logger.error(f"❌ Falló conexión PostgreSQL: {e}")
            # Fallback a SQLite
    
    # 2. Fallback a SQLite (Local)
    BACKEND = "sqlite"
    logger.info("⚠️ Usando SQLite (Local Fallback)")
    return True

@contextmanager
def get_cursor():
    """Obtiene un cursor agnóstico (Postgres o SQLite)"""
    conn = None
    try:
        if BACKEND == "postgres" and _pg_pool:
            conn = _pg_pool.getconn()
            yield conn.cursor()
            conn.commit()
        else:
            # SQLite Mode
            conn = sqlite3.connect("local_fallback.db")
            # Emular placeholder %s de Postgres
            # SQLite usa ?, así que reemplazamos al vuelo en execute?
            # Mejor: Usamos un wrapper simple
            yield SQLiteCursorWrapper(conn.cursor())
            conn.commit()
            
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"❌ Error DB ({BACKEND}): {e}")
        yield None
    finally:
        if BACKEND == "postgres" and conn:
            _pg_pool.putconn(conn)
        elif BACKEND == "sqlite" and conn:
            conn.close()

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
    """Crea tablas si no existen"""
    try:
        with get_cursor() as cur:
            if not cur: return False
            
            # Syntax compatible (Postgres / SQLite)
            # SERIAL vs AUTOINCREMENT es la diferencia principal
            # Usaremos sintaxis condicional
            
            if BACKEND == "postgres":
                id_type = "SERIAL PRIMARY KEY"
                timestamp_default = "CURRENT_TIMESTAMP"
            else:
                id_type = "INTEGER PRIMARY KEY AUTOINCREMENT"
                timestamp_default = "CURRENT_TIMESTAMP"
            
            sql = f'''
                CREATE TABLE IF NOT EXISTS visitors (
                    id {id_type},
                    external_id TEXT NOT NULL,
                    fbclid TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    source TEXT,
                    timestamp TIMESTAMP DEFAULT {timestamp_default}
                );
            '''
            cur.execute(sql)
            
            # Indices
            cur.execute('CREATE INDEX IF NOT EXISTS idx_visitors_external_id ON visitors(external_id);')
            cur.execute('CREATE INDEX IF NOT EXISTS idx_visitors_fbclid ON visitors(fbclid);')
            
        logger.info(f"✅ Tablas inicializadas ({BACKEND})")
        return True
    except Exception as e:
        logger.error(f"❌ Error creando tablas: {e}")
        return False

# =================================================================
# OPERATIONS
# =================================================================

def save_visitor(external_id, fbclid, ip_address, user_agent, source="pageview"):
    with get_cursor() as cur:
        if cur:
            cur.execute(
                "INSERT INTO visitors (external_id, fbclid, ip_address, user_agent, source) VALUES (%s, %s, %s, %s, %s)",
                (external_id, fbclid, ip_address, user_agent[:500] if user_agent else None, source)
            )

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

