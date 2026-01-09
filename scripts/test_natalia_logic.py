
import sys
import os
import logging

# Add core to path
sys.path.append(os.path.join(os.getcwd(), 'core'))

# Mock database to avoid connection errors if DB is unreachable
from unittest.mock import MagicMock, patch

# Config logging
logging.basicConfig(level=logging.INFO)

def test_natalia_brain():
    print("🧠 Testing Natalia Brain Logic...")
    
    # Mock database functions so we don't need real DB
    with patch('app.natalia.get_or_create_lead') as mock_get_lead, \
         patch('app.natalia.log_interaction') as mock_log:
        
        mock_get_lead.return_value = "mock_lead_id_123"
        mock_log.return_value = True
        
        from app.natalia import natalia
        
        # Test Case 1: Greeting
        print("\nCaso 1: Saludo")
        res1 = natalia.process_message("59112345678", "Hola Natalia", {"name": "Test User"})
        print(f"Reply: {res1['reply']}")
        assert "Hola! Soy Natalia" in res1['reply'] or "ayudarte" in res1['reply']
        
        # Test Case 2: Price
        print("\nCaso 2: Precio")
        res2 = natalia.process_message("59112345678", "cuanto es el precio del microblading?")
        print(f"Reply: {res2['reply']}")
        assert "150" in res2['reply']
        
        # Test Case 3: Location
        print("\nCaso 3: Ubicación")
        res3 = natalia.process_message("59112345678", "donde estan ubicados?")
        print(f"Reply: {res3['reply']}")
        assert "Tucumán" in res3['reply']
        
        print("\n✅ All Logic Tests Passed!")

if __name__ == "__main__":
    test_natalia_brain()
