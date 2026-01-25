
def test_ping(client):
    """Verifica que el endpoint más básico responda PONG"""
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.text == "pong"

def test_health_check(client):
    """
    Verifica el endpoint de salud completo.
    Debe retornar 200 y el estado de la base de datos.
    """
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "database" in data
    # No fallamos si la DB no está configurada en CI, pero verificamos que la key exista
