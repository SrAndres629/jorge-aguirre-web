
def test_homepage_loads(client):
    """Verifica que la página de inicio cargue (200 OK)"""
    response = client.get("/")
    assert response.status_code == 200

def test_homepage_content(client):
    """
    Verifica que el contenido clave esté presente.
    Esto valida que la refactorización de templates funcionó.
    """
    response = client.get("/")
    content = response.text
    
    # 1. Verificar Título SEO
    assert "<title>Jorge Aguirre Flores" in content
    
    # 2. Verificar que se renderizó la Navbar (componente)
    assert 'id="mainNav"' in content
    
    # 3. Verificar sección crítica (Servicios)
    assert 'id="servicios"' in content
