
from app.agents.base import BaseAgent
from typing import Dict, Any, List

class ChiefAgent(BaseAgent):
    """
    The Business Owner (Jorge).
    Goal: Approval, Business Insights, Override.
    """
    def __init__(self, phone: str, context: Dict[str, Any]):
        super().__init__(phone, context)
        self.role_name = "SUPERVISOR"

    def get_allowed_tools(self) -> List[str]:
        return ["approve_discount", "get_sales_report", "get_sales_forecast", "update_loyalty_tier"]

    def get_system_prompt(self) -> str:
        return (
            f"Hola Jorge. Soy Natalia, tu secretaria virtual. "
            f"Estoy aquí para reportarte citas, pedirte autorización para descuentos "
            f"y darte métricas de negocio. Hablamos de negocio."
        )

    async def process(self, text: str, tools: List[Dict]) -> Dict[str, Any]:
        pass
