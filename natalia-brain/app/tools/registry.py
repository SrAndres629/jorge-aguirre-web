import inspect
import functools
from typing import Callable, Dict, Any, List
import logging


logger = logging.getLogger("ToolRegistry")

class ToolRegistry:
    """
    Engine for registering Python functions as LLM Tools.
    Auto-generates Gemini-compatible JSON schemas from type hints.
    """
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._schemas: List[Dict[str, Any]] = []

    def register(self, roles: List[str] = None):
        """
        Decorator to register a function with optional role-based access.
        Usage: 
            @registry.register(roles=["GOD", "CHIEF"])
            def my_tool(a: int): ...
            
            @registry.register # Public tool
            def public_tool(): ...
        """
        def decorator(func: Callable):
            # Get function metadata
            name = func.__name__
            doc = func.__doc__ or "No description provided."
            
            # Analyze signature for schema generation
            sig = inspect.signature(func)
            parameters = {
                "type": "OBJECT",
                "properties": {},
                "required": []
            }
            
            for param_name, param in sig.parameters.items():
                if param_name == "self": continue
                
                # Map Python types to Gemini Schema types
                p_type = "STRING" # Default
                if param.annotation == int: p_type = "INTEGER"
                elif param.annotation == float: p_type = "NUMBER"
                elif param.annotation == bool: p_type = "BOOLEAN"
                
                parameters["properties"][param_name] = {
                    "type": p_type,
                    "description": f"Parameter {param_name}" # Ideally parse from docstring
                }
                
                if param.default == inspect.Parameter.empty:
                    parameters["required"].append(param_name)

            # Create Gemini Tool Definition
            tool_def = {
                "name": name,
                "description": doc.strip(),
                "parameters": parameters
            }

            self._tools[name] = func
            # Store roles metadata
            tool_def["_roles"] = roles
            self._schemas.append(tool_def)
            
            logger.info(f"🔧 Tool Registered: {name} | Roles: {roles or 'ALL'}")
            return func
        return decorator

    def get_tools_for_gemini(self, user_role: str = None) -> List[Dict[str, Any]]:
        """Returns the list of function declarations filtered by role."""
        filtered_schemas = []
        for schema in self._schemas:
            allowed_roles = schema.get("_roles")
            # If no roles defined, it's public. If roles defined, user must have one.
            if not allowed_roles or (user_role and user_role in allowed_roles):
                # Return schema without internal metadata
                clean_schema = {k:v for k,v in schema.items() if k != "_roles"}
                filtered_schemas.append(clean_schema)
        
        return filtered_schemas

    def execute(self, name: str, args: Dict[str, Any]):
        """Safely executes the tool by name."""
        if name not in self._tools:
            raise ValueError(f"Tool {name} not found.")
        
        try:
            logger.info(f"🔨 Executing Tool: {name} with {args}")
            result = self._tools[name](**args)
            logger.info(f"✅ Tool Result: {result}")
            return result
        except Exception as e:
            logger.error(f"❌ Tool Failure ({name}): {e}")
            return f"Error executing tool {name}: {str(e)}"

# Singleton Instance
registry = ToolRegistry()
