from datetime import datetime
from app.tools.registry import registry

@registry.register
def get_current_date() -> str:
    """
    Returns the current date and time in string format.
    Use this when the user asks 'what day is it' or 'schedule for tomorrow'.
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@registry.register
def calculate_price_estimate(service_type: str) -> str:
    """
    Calculates the estimated price for a service.
    Args:
        service_type: The type of service (brows, lips, eyes).
    """
    service_type = service_type.lower()
    if "brow" in service_type or "ceja" in service_type:
        return "Estimated range for Brows: 1500 - 2000 BOB"
    elif "lip" in service_type or "labio" in service_type:
        return "Estimated range for Lips: 1800 - 2200 BOB"
    else:
        return "Service not found. Standard audit fee is 200 BOB."
