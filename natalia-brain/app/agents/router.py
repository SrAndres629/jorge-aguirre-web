
from typing import Dict, Any, Optional
from app.agents.base import BaseAgent
from app.agents.sales import SalesAgent
from app.agents.god import GodAgent
from app.agents.chief import ChiefAgent # Need to create this
from app.roles import Role

# Config
ADMIN_PHONE = "59178113055"
CHIEF_PHONE = "59176863944"

class RoleRouter:
    """
    Factory Pattern for Cognitive Agents.
    Determines WHO is talking and instantiates the correct Brain Strategy.
    """
    
    @staticmethod
    def get_agent(phone: str, context: Optional[Dict[str, Any]] = None) -> BaseAgent:
        clean = "".join(filter(str.isdigit, phone))
        ctx = context or {}

        if clean == ADMIN_PHONE:
            return GodAgent(clean, ctx)
        
        elif clean == CHIEF_PHONE:
            # Placeholder until Chief file created
            return ChiefAgent(clean, ctx) 
            
        else:
            return SalesAgent(clean, ctx)
