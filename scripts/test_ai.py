import requests
import json

URL = "http://localhost:8000/chat/incoming"

def test_chat(text, user="Cliente Prueba"):
    payload = {
        "phone": "59100000000",
        "text": text,
        "name": user
    }
    try:
        resp = requests.post(URL, json=payload)
        data = resp.json()
        print(f"\n🙋 USER: {text}")
        print(f"🤖 NATALIA 2.0:\n{data.get('reply', 'ERROR')}")
        print("-" * 50)
    except Exception as e:
        print(e)
        
if __name__ == "__main__":
    # Test 1: Intención clara con complejidad (trabajo previo)
    test_chat("Hola Natalia, quiero saber el precio de unas cejas. Tengo un tatuaje viejo horrible.")
    
    # Test 2: Pregunta casual de ubicación
    test_chat("Y donde quedan?")
