
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
        # Simplified for now, in production this comes from DB
        return (
            f"Eres NATALIA, la asistente virtual de Jorge Aguirre (Esteticista). "
            f"Tu tono es cálido, profesional y persuasivo (Ventas). "
            f"Tu objetivo es agendar citas para Microblading. "
            f"Nunca inventes precios. Usa tus herramientas. "
            f"Hablas con el cliente: {self.phone}."
        )

    async def process(self, text: str, tools: List[Dict]) -> Dict[str, Any]:
        # Here we would invoke the LLM logic specific to Sales
        # For the prototype, we delegate back to the shared 'natalia.py' logic 
        # or implement a specific loop?
        # To follow the Master Order strictly: "RoleRouter instancie el agente correcto".
        
        # For now, this class defines the CONFIGURATION (Prompt + Tools).
        # The execution logic might still reside in the Brain or be moved here.
        pass
