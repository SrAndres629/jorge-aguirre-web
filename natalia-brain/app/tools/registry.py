
import logging
import inspect
from typing import Callable, Dict, Any, List, Optional

logger = logging.getLogger("ToolRegistry")

class ToolRegistry:
    """
    Cognitive Tool Registry (v4.1)
    Supports: 
    1. Decorator style: @registry.register
    2. parameterized decorator: @registry.register(roles=["GOD"])
    3. Explicit registration: registry.register("name", func, roles, definition)
    """
    def __init__(self):
        self._tools: Dict[str, Dict[str, Any]] = {}

    def register(self, name_or_func: Any = None, func: Optional[Callable] = None, roles: List[str] = None, definition: Dict[str, Any] = None):
        """
        Multimodal registration.
        - As @registry.register
        - As @registry.register(roles=["ADMIN"])
        - As registry.register("name", func, roles, def)
        """
        
        # 1. Handle explicit call: registry.register("name", func, roles, def)
        if isinstance(name_or_func, str) and func is not None:
            self._tools[name_or_func] = {
                "func": func,
                "roles": roles or [],
                "definition": definition or self._auto_generate_schema(func, name_or_func)
            }
            logger.info(f"🔧 Tool Registered (Explicit): {name_or_func} | Roles: {roles}")
            return func

        # 2. Handle decorator factory: @registry.register(roles=["ADMIN"])
        def decorator(f: Callable):
            name = f.__name__
            self._tools[name] = {
                "func": f,
                "roles": roles or [],
                "definition": definition or self._auto_generate_schema(f, name)
            }
            logger.info(f"🔧 Tool Registered (Decorator): {name} | Roles: {roles}")
            return f

        # Case 3: @registry.register (no params)
        if callable(name_or_func):
            return decorator(name_or_func)

        # Case 4: @registry.register(roles=[...]) -> returns decorator
        return decorator

    def _auto_generate_schema(self, func: Callable, name: str) -> Dict[str, Any]:
        """Introspects function to create Gemini schema."""
        doc = func.__doc__ or "No description provided."
        sig = inspect.signature(func)
        
        parameters = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        for p_name, p in sig.parameters.items():
            if p_name == 'self': continue
            
            p_type = "string"
            if p.annotation == int: p_type = "integer"
            elif p.annotation == float: p_type = "number"
            elif p.annotation == bool: p_type = "boolean"
            
            parameters["properties"][p_name] = {
                "type": p_type,
                "description": f"Parameter {p_name}"
            }
            if p.default == inspect.Parameter.empty:
                parameters["required"].append(p_name)
                
        return {
            "name": name,
            "description": doc.strip(),
            "parameters": parameters
        }

    def get_tools_by_names(self, names: List[str]) -> List[Dict[str, Any]]:
        return [self._tools[n]["definition"] for n in names if n in self._tools]

    def execute(self, name: str, args: Dict[str, Any]) -> Any:
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

# --- SYSTEM TOOLS INITIALIZATION ---
# These are the official tools required by Phase 4
from app.tools.admin_tools import run_readonly_sql
from app.tools.crm_tools import check_availability

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
