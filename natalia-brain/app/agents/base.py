
from abc import ABC, abstractmethod
from typing import Dict, Any, List
import logging

logger = logging.getLogger("BaseAgent")

class BaseAgent(ABC):
    """
    Abstract Base Class for all Cognitive Agents.
    Enforces the 'System of Thought' contract.
    """
    
    def __init__(self, phone: str, context: Dict[str, Any]):
        self.phone = phone
        self.context = context
        self.role_name = "BASE"

    @abstractmethod
    async def process(self, text: str, tools: List[Dict]) -> Dict[str, Any]:
        """
        Core cognitive loop.
        Must return a structured response dictionary.
        """
        pass

    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Returns the specific 'Soul' (Persona) of the agent.
        """
        pass

    @abstractmethod
    def get_allowed_tools(self) -> List[str]:
        """
        Returns list of tool names this agent is permitted to use.
        """
        pass
