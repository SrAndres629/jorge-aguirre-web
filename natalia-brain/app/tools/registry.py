import inspect
import functools
from typing import Callable, Dict, Any, List
from pydantic import ValidateCallWrapper
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

    def register(self, func: Callable):
        """
        Decorator to register a function.
        Usage: 
            @registry.register
            def my_tool(a: int): ...
        """
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
        self._schemas.append(tool_def)
        
        logger.info(f"🔧 Tool Registered: {name}")
        return func

    def get_tools_for_gemini(self):
        """Returns the list of function declarations for the model."""
        # Gemini expects: tools=[{ "function_declarations": [...] }]
        return self._schemas

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
