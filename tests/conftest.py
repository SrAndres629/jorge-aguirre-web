
import sys
import os
# Add the 'core' directory to sys.path so we can import 'app' module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../core')))

import pytest
from fastapi.testclient import TestClient

from main import app # Import 'app' object from 'main.py' in core root


@pytest.fixture(scope="module")
def client():
    """
    Fixture global para el cliente de pruebas.
    Permite hacer peticiones HTTP simuladas al servidor FastAPI.
    """
    with TestClient(app) as test_client:
        yield test_client
