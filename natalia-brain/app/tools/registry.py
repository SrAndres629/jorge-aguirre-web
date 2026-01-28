
import logging
from typing import Callable, Dict, Any, List

logger = logging.getLogger("ToolRegistry")

class ToolRegistry:
    """
    Unified Tool Registry for polymorphic agents.
    Manages tools and their role-based permissions.
    """
    def __init__(self):
        self._tools: Dict[str, Dict[str, Any]] = {}

    def register(self, name: str, func: Callable, roles: List[str], definition: Dict[str, Any]):
        """Explicitly register a tool with its allowed roles and Gemini definition."""
        self._tools[name] = {
            "func": func,
            "roles": roles,
            "definition": definition
        }
        logger.info(f"🔧 Tool Registered: {name} | Roles: {roles}")

    def get_tools_by_names(self, names: List[str]) -> List[Dict[str, Any]]:
        """Returns Gemini-compatible definitions for a subset of tools."""
        return [self._tools[n]["definition"] for n in names if n in self._tools]

    def execute(self, name: str, args: Dict[str, Any]) -> Any:
        """Executes a tool by name with provided arguments."""
        if name not in self._tools:
            return f"Error: Tool {name} not found."
        
        try:
            logger.info(f"🔨 [TOOL EXEC] {name} | Args: {args}")
            return self._tools[name]["func"](**args)
        except Exception as e:
            logger.error(f"❌ Tool Failure ({name}): {e}")
            return f"Error: {str(e)}"

# Singleton Instance
registry = ToolRegistry()

# --- TOOL REGISTRY INITIALIZATION ---
from app.tools.admin_tools import run_readonly_sql
from app.tools.crm_tools import check_availability

# 1. SQL Tool
registry.register(
    "run_readonly_sql",
    run_readonly_sql,
    roles=["GOD"],
    definition={
        "name": "run_readonly_sql",
        "description": "Ejecuta una consulta SQL SELECT para auditoría del sistema. Solo modo Admin.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "La consulta SELECT SQL."}
            },
            "required": ["query"]
        }
    }
)

# 2. Availability Tool
registry.register(
    "check_availability",
    check_availability,
    roles=["CLIENT", "SUPERVISOR", "GOD"],
    definition={
        "name": "check_availability",
        "description": "Consulta disponibilidad de citas en la agenda.",
        "parameters": {
            "type": "object",
            "properties": {
                "service_name": {"type": "string", "description": "Ej. 'microblading'"}
            },
            "required": ["service_name"]
        }
    }
)
