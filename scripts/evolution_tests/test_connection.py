import httpx
import asyncio
import getpass

async def check_api(base_url, api_key):
    print(f"\n🔍 Conectando a Evolution API: {base_url}")
    print(f"🔑 Usando API Key: {'*' * len(api_key)}")

    headers = {
        "apikey": api_key,
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        # 1. Check Health (Root or simple endpoint)
        try:
            print("\n📡 Test 1: Ping al Servidor...")
            resp = await client.get(base_url.rstrip("/"), timeout=10.0)
            print(f"   [GET /] Status: {resp.status_code}")
            if resp.status_code == 200:
                print("   ✅ El servidor está ONLINE y respondiendo.")
            else:
                print("   ⚠️ El servidor responde, pero con un código inesperado.")
        except Exception as e:
            print(f"   ❌ Error conectando al servidor: {e}")
            return

        # 2. Check Authentication using fetchInstances
        try:
            print("\n🔐 Test 2: Verificando API Key...")
            url = f"{base_url.rstrip('/')}/instance/fetchInstances"
            resp = await client.get(url, headers=headers, timeout=10.0)
            
            if resp.status_code == 200:
                print("   ✅ Autenticación EXITOSA.")
                instances = resp.json()
                print(f"   📊 Instancias encontradas: {len(instances)}")
                print(json.dumps(instances, indent=2))
            elif resp.status_code == 401 or resp.status_code == 403:
                print("   ❌ FALLO DE AUTENTICACIÓN. Revisa tu Global API Key.")
            else:
                print(f"   ⚠️ Error inesperado ({resp.status_code}): {resp.text}")
        except Exception as e:
            print(f"   ❌ Error en autenticación: {e}")

if __name__ == "__main__":
    import json
    print("=== 🦅 Evolution API Auditor (Remote) ===")
    
    default_url = input("Ingrese URL de Render (ej: https://evo.onrender.com): ").strip()
    if not default_url:
        print("❌ URL necesaria.")
        exit()

    default_key = input("Ingrese Global API Key (Enter para usar 'JorgeSecureKey123'): ").strip()
    if not default_key:
        default_key = "JorgeSecureKey123"

    asyncio.run(check_api(default_url, default_key))
