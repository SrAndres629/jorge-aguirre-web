
from app.agents.base import BaseAgent
from typing import Dict, Any, List
import logging

logger = logging.getLogger("SalesAgent")

class SalesAgent(BaseAgent):
    """
    The 'Face' of the business.
    Goal: Conversion, Empathy, Scheduling.
    Security: HIGH (Safety filters on).
    """

    def __init__(self, phone: str, context: Dict[str, Any]):
        super().__init__(phone, context)
        self.role_name = "CLIENT"

    def get_allowed_tools(self) -> List[str]:
        # Clients can only use safe tools (availability, pricing)
        return ["check_availability", "get_services_prices"]

    def get_system_prompt(self) -> str:
        return (
            f"Eres NATALIA, asistente experta en ventas de Jorge Aguirre. "
            f"Tu tono es amable, persuasivo y enfocado en el cierre de ventas. "
            f"Si detectas a un número desconocido, preséntate como la asistente comercial. "
            f"Tu objetivo es resolver dudas sobre Microblading y agendar citas."
        )

    async def process(self, text: str, tools: List[Dict]) -> Dict[str, Any]:
        # Here we would invoke the LLM logic specific to Sales
        # For the prototype, we delegate back to the shared 'natalia.py' logic 
        # or implement a specific loop?
        # To follow the Master Order strictly: "RoleRouter instancie el agente correcto".
        
        # For now, this class defines the CONFIGURATION (Prompt + Tools).
        # The execution logic might still reside in the Brain or be moved here.
        pass
