"""
Ventas Doctoral: Dynamic Pricing Engine
Algorithmic Yield Management for Maximized Margins
"""

from typing import Dict, Optional
import math

class PricingEngine:
    """
    Adjusts product pricing based on supply, demand, and user value parameters.
    """
    
    def __init__(self, base_price: float, min_margin_factor: float = 1.2):
        self.base_price = base_price
        self.min_price = base_price * min_margin_factor

    def calculate_dynamic_price(self, 
                                demand_index: float, 
                                competitor_avg: Optional[float] = None,
                                user_loyalty_tier: str = "Standard") -> float:
        """
        Calculates optimized price using elasticity logic.
        
        :param demand_index: 1.0 (Normal) to 2.0 (High)
        :param competitor_avg: Optional competitor data for market alignment
        :param user_loyalty_tier: Tier from CRM Maestro (Champions get discounts)
        """
        
        # 1. Demand Surcharge (Exponential uplift for high demand)
        demand_modifier = math.pow(demand_index, 1.5)
        price = self.base_price * demand_modifier
        
        # 2. Competitor Check (Don't exceed 20% of market average unless value is premium)
        if competitor_avg and price > (competitor_avg * 1.25):
            price = competitor_avg * 1.25
            
        # 3. CRM Integration (Loyalty Rewards)
        loyalty_discounts = {
            "Champions": 0.15,
            "Loyal Customers": 0.10,
            "Potential Loyalists": 0.05,
            "Standard": 0.0
        }
        discount = loyalty_discounts.get(user_loyalty_tier, 0.0)
        price = price * (1 - discount)
        
        # 4. Global Minimum Enforcement
        return max(price, self.min_price)

if __name__ == "__main__":
    engine = PricingEngine(base_price=100.0)
    print(f"Standard Price: ${engine.calculate_dynamic_price(1.0)}")
    print(f"High Demand (Champion): ${engine.calculate_dynamic_price(1.8, user_loyalty_tier='Champions')}")
    print(f"High Demand (At Risk): ${engine.calculate_dynamic_price(1.8, user_loyalty_tier='Standard')}")
