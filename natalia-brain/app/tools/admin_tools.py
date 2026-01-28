
from typing import Dict, Any
import logging
from app.database import get_cursor

logger = logging.getLogger("SQLTool")

def run_readonly_sql(query: str) -> str:
    """
    Executes a raw SQL SELECT query in the database.
    RESTRICTED: Only for RootAgent.
    """
    if not query.strip().lower().startswith("select"):
        return "Error: Only SELECT queries are allowed for safety."
        
    try:
        with get_cursor() as cur:
            cur.execute(query)
            # Fetch column names
            colnames = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
            
            if not rows:
                return "Query executed successfully. Result: No rows found."
                
            # Format as a simple table string
            result = [f"| {' | '.join(colnames)} |"]
            result.append(f"| {' | '.join(['---'] * len(colnames))} |")
            for row in rows[:10]: # Limit to 10 rows for context window
                result.append(f"| {' | '.join(map(str, row))} |")
                
            return "\n".join(result)
    except Exception as e:
        logger.error(f"❌ SQL Execution Failed: {e}")
        return f"Error: {str(e)}"
