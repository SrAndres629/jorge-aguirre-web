
from app.agents.base import BaseAgent
from typing import Dict, Any, List
import logging

class GodAgent(BaseAgent):
    """
    The 'Root' user (You).
    Goal: System Management, Debugging, SQL.
    Security: NONE (Full Access).
    """

    def __init__(self, phone: str, context: Dict[str, Any]):
        super().__init__(phone, context)
        self.role_name = "GOD"

    def get_allowed_tools(self) -> List[str]:
        # God Mode: Critical Tools
        return ["run_readonly_sql", "get_system_status", "restart_server"]

    def get_system_prompt(self) -> str:
        return (
            f"ERES NATALIA EN 'MODO ADMIN/ROOT'. "
            f"Estás hablando con tu creador (Andrés). "
            f"Usa un tono técnico, lacónico y eficiente. "
            f"Tienes acceso total al sistema y herramientas SQL. "
            f"Confirma siempre que estás operando en Nivel Root."
        )

    async def process(self, text: str, tools: List[Dict]) -> Dict[str, Any]:
        pass
