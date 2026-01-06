
import httpx
import asyncio
from typing import Dict, Any, Optional
from .config import settings, get_logger

logger = get_logger("Client")

class EvolutionClient:
    """
    Cliente base asincrónico para Evolution API con manejo robusto de errores.
    """
    def __init__(self):
        self.base_url = settings.evolution_api_url.rstrip('/')
        self.headers = {
            "apikey": settings.evolution_api_key,
            "Content-Type": "application/json"
        }
        # Singleton http client could be managed here or per request depending on usage
    
    async def _request(self, method: str, endpoint: str, payload: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Ejecuta una petición HTTP con manejo centralizado de excepciones y códigos de estado.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                logger.debug(f"{method} -> {url}")
                
                response = await client.request(
                    method=method, 
                    url=url, 
                    json=payload, 
                    headers=self.headers
                )
                
                # Manejo de códigos de estado específicos de HTTP
                response.raise_for_status()
                
                # Intentar parsear JSON
                try:
                    return response.json()
                except ValueError:
                    # Si no es JSON (ej: string simple), devolverlo en estructura estándar
                    return {"status": "success", "data": response.text}

        except httpx.HTTPStatusError as e:
            # 4xx y 5xx
            status = e.response.status_code
            error_text = e.response.text
            logger.error(f"API Error {status}: {error_text}")
            
            if status == 401:
                return {"error": True, "code": 401, "message": "Unauthorized: Invalid API Key"}
            elif status == 404:
                return {"error": True, "code": 404, "message": "Endpoint or Resource Not Found"}
            
            return {"error": True, "code": status, "message": error_text}
            
        except httpx.RequestError as e:
            # Errores de red, DNS, Timeout
            logger.error(f"Network Error: {str(e)}")
            return {"error": True, "code": 0, "message": f"Network Error: {str(e)}"}
            
        except Exception as e:
            # Errores inesperados
            logger.exception("Unexpected internal error")
            return {"error": True, "code": -1, "message": str(e)}

    # Métodos Helper genéricos
    async def get(self, endpoint: str):
        return await self._request("GET", endpoint)

    async def post(self, endpoint: str, data: Dict):
        return await self._request("POST", endpoint, payload=data)

    async def delete(self, endpoint: str):
        return await self._request("DELETE", endpoint)
