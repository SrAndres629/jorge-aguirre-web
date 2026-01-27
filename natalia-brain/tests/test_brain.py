import pytest
from unittest.mock import AsyncMock, patch
from app.natalia import NataliaBrain

@pytest.fixture
def brain():
    return NataliaBrain()

@pytest.mark.asyncio
async def test_role_detection_root(brain):
    # ADMIN_PHONE = "59178113055"
    with patch("app.natalia.get_or_create_lead", return_value=(1, False)), \
         patch("app.natalia.log_interaction"), \
         patch("app.natalia.get_chat_history", return_value=[]), \
         patch.object(NataliaBrain, "_generate_thought", new_callable=AsyncMock) as mock_thought:
        
        mock_thought.return_value = "Hola Admin"
        result = await brain.process_message("59178113055", "Hola")
        
        assert result["metadata"]["role"] == "ROOT"
        assert result["reply"] == "Hola Admin"

@pytest.mark.asyncio
async def test_role_detection_client(brain):
    with patch("app.natalia.get_or_create_lead", return_value=(2, True)), \
         patch("app.natalia.log_interaction"), \
         patch("app.natalia.get_chat_history", return_value=[]), \
         patch.object(NataliaBrain, "_generate_thought", new_callable=AsyncMock) as mock_thought:
        
        mock_thought.return_value = "Hola Cliente"
        result = await brain.process_message("123456789", "Quiero info")
        
        assert result["metadata"]["role"] == "CLIENT"
        assert result["is_new_lead"] is True

@pytest.mark.asyncio
async def test_intent_classification_microblading(brain):
    with patch("app.natalia.get_or_create_lead", return_value=(3, False)), \
         patch("app.natalia.log_interaction"), \
         patch("app.natalia.get_chat_history", return_value=[]), \
         patch.object(NataliaBrain, "_generate_thought", new_callable=AsyncMock) as mock_thought:
        
        mock_thought.return_value = "Claro, sobre cejas..."
        result = await brain.process_message("123456789", "Me interesan las cejas")
        
        assert result["metadata"]["intent"] == "microblading"
        assert result["metadata"]["value"] == 300.0

@pytest.mark.asyncio
async def test_error_handling(brain):
    with patch("app.natalia.get_or_create_lead", return_value=(4, False)), \
         patch("app.natalia.log_interaction"), \
         patch("app.natalia.get_chat_history", side_effect=Exception("Database down")):
        
        # When an exception happens in process_message, it should return a fallback message
        result = await brain.process_message("123456789", "Hola")
        assert "disculpa" in result["reply"].lower()
