
from typing import Dict, Any
import logging

logger = logging.getLogger("ScheduleTool")

def check_availability(service_name: str) -> str:
    """
    Checks the availability for a specific service.
    Accessible by SalesAgent.
    """
    # Placeholder logic - in production this would query a Google Calendar or DB
    logger.info(f"📅 Checking availability for {service_name}")
    
    # Mocking a response for the surjectivity proof
    if "micro" in service_name.lower():
        return "Hay disponibilidad para Microblading este Jueves a las 15:00 y Viernes a las 10:00."
    return "Tengo disponibilidad general toda la semana para consultas de valoración."
