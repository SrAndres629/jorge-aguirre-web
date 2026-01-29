
from app.agents.base import BaseAgent
from typing import Dict, Any, List
import logging
import sys
import os

logger = logging.getLogger("SalesAgent")

# Dynamic import setup for Skills
# Assuming run from root of jorge_web or pythonpath includes it
SKILL_PATH = os.path.join(os.getcwd(), ".agent", "skills")

class SalesAgent(BaseAgent):
    """
    The 'Face' of the business.
    Goal: Conversion, Empathy, Scheduling.
    Security: HIGH (Safety filters on).
    Capabilities: Uses '.agent/skills/crm-maestro' for segmentation.
    """

    def __init__(self, phone: str, context: Dict[str, Any]):
        super().__init__(phone, context)
        self.role_name = "CLIENT"

    def get_allowed_tools(self) -> List[str]:
        return ["check_availability", "get_services_prices", "check_loyalty_tier"]

    def get_system_prompt(self) -> str:
        # Dynamic CRM Context Injection
        tier = self._get_loyalty_tier()
        
        base_prompt = (
            f"Eres NATALIA, asistente experta en ventas de Jorge Aguirre. "
            f"Tu tono es amable, persuasivo y enfocado en el cierre de ventas. "
        )
        
        if tier == "VIP":
            base_prompt += f" TRATO VIP: Este cliente es muy importante. Ofrécele prioridad en agenda."
        
        return base_prompt

    def _get_loyalty_tier(self) -> str:
        """
        Executes the Segmentation Engine from .agent/skills
        Currently a mock/placeholder wrapper until we fully bridge the python execution env.
        """
        # TODO: Implement actual subprocess call to segmentation_engine.py
        # For now, safe default.
        return "STANDARD"

    async def process(self, text: str, tools: List[Dict]) -> Dict[str, Any]:
        # The Brain (LLM) processing logic would go here.
        # This structure ensures the Agent is configured correctly.
        pass
