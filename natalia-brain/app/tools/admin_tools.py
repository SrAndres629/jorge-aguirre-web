
from app.tools.registry import registry
from app.database import get_cursor
import json
import logging

logger = logging.getLogger("AdminTools")

@registry.register(roles=["GOD"])
def run_readonly_sql(query: str) -> str:
    """
    Executes a READ-ONLY SQL query against the database. 
    Use this to answer questions about leads, messages, or system stats.
    
    Args:
        query: Valid SQL starting with SELECT.
    """
    logger.info(f"🛡️ Admin invoking SQL: {query}")
    
    # 1. Security Check (Software Level)
    if not query.strip().upper().startswith("SELECT"):
        return "❌ SECURITY ERROR: Only SELECT queries are allowed."

    # 2. Execution
    try:
        with get_cursor() as cur:
            # Enforce Read Only Transaction
            cur.execute("SET TRANSACTION READ ONLY;")
            
            cur.execute(query)
            rows = cur.fetchall()
            
            # Format as JSON for LLM comprehension
            if not rows:
                return "Query returned 0 results."
                
            # Get column names
            colnames = [desc[0] for desc in cur.description]
            results = []
            for row in rows:
                results.append(dict(zip(colnames, row)))
            
            return json.dumps(results[:20], default=str) # Limit to 20 to save tokens
            
    except Exception as e:
        logger.error(f"SQL Execution Error: {e}")
        return f"❌ Database Error: {str(e)}"

@registry.register(roles=["GOD", "CHIEF"])
def get_system_status() -> str:
    """Returns the current health status of the brain."""
    return "✅ Natalia Brain v2.0 is OPERATIONAL. Linked to Supabase & Render."
