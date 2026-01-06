
import pytest
import sys
import os

# Add the parent directory to sys.path to ensure modules are found
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from scripts.maintenance.evolution_mcp.client import EvolutionClient
from scripts.maintenance.evolution_mcp.tools import messaging, instances, social, webhooks

def test_imports():
    """Verify that all modules can be imported without error."""
    assert messaging is not None
    assert instances is not None
    assert social is not None
    assert webhooks is not None

def test_client_init():
    """Verify client initialization."""
    client = EvolutionClient()
    # Mask key for log safety if printed
    assert client.headers.get("apikey") == "B89599B2-37E4-4DCA-92D3-87F8674C7D69"
    assert "evolution_api" in client.base_url or "localhost" in client.base_url
