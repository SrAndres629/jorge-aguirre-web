# =================================================================
# MAIN.PY - Entry Point (Thin Wrapper)
# Jorge Aguirre Flores Web
# =================================================================
# 
# Este archivo es un punto de entrada limpio que:
# 1. Configura la aplicación FastAPI
# 2. Monta los archivos estáticos
# 3. Incluye todos los routers modulares
# 4. Inicializa la base de datos
#
# La lógica de negocio está en el paquete app/
# =================================================================

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.gzip import GZipMiddleware
import uvicorn
import logging

# Módulos internos
from app.config import settings
from app import database
from app.routes import pages, tracking_routes, admin, health

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =================================================================
# APLICACIÓN FASTAPI
# =================================================================

app = FastAPI(
    title="Jorge Aguirre Flores Web",
    description="Sitio web profesional con tracking Meta CAPI",
    version="2.0.0"
)

# Middleware GZip para compresión (5x más rápido en móviles)
app.add_middleware(GZipMiddleware, minimum_size=500)

# Middleware para Proxy/CDN (Cloudflare/Render)
# Confía en headers X-Forwarded-For y X-Forwarded-Proto
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts=["*"])

# Middleware CORS (Seguridad: permitir solo dominios propios)
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://jorgeaguirreflores.com", 
        "https://www.jorgeaguirreflores.com", 
        "http://localhost:8000",
        "http://localhost:8081",
        "http://localhost:5678"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =================================================================
# SECURITY: RATE LIMITING
# =================================================================
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Inicializar Linkiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Aplicar límite global (opcional, o por ruta)
# app.add_middleware(SlowAPIMiddleware)

# =================================================================
# ARCHIVOS ESTÁTICOS CON CACHE AGRESIVO
# =================================================================

from starlette.staticfiles import StaticFiles as StarletteStaticFiles
from starlette.responses import Response
import os

class CachedStaticFiles(StarletteStaticFiles):
    """StaticFiles con headers de caché agresivos para WPO"""
    
    async def get_response(self, path: str, scope) -> Response:
        response = await super().get_response(path, scope)
        
        # Agregar Cache-Control a todos los recursos
        ext = os.path.splitext(path)[1].lower()
        
        # Imágenes, CSS, JS: caché de 1 año (inmutable)
        if ext in ['.webp', '.png', '.jpg', '.jpeg', '.gif', '.svg', 
                   '.css', '.js', '.woff', '.woff2']:
            response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
        else:
            # Otros archivos: caché más corto
            response.headers['Cache-Control'] = 'public, max-age=86400'
        
        return response

# Montar archivos estáticos con caché
app.mount("/static", CachedStaticFiles(directory="static"), name="static")


# =================================================================
# ROUTERS
# =================================================================

# Páginas HTML
app.include_router(pages.router)

# Tracking endpoints (/track-lead, /track-viewcontent)
app.include_router(tracking_routes.router)

# Panel de administración (/admin/*)
app.include_router(admin.router)

# Health checks (/health, /ping)
app.include_router(health.router)


# =================================================================
# EVENTOS DE CICLO DE VIDA
# =================================================================

@app.on_event("startup")
async def startup_event():
    """Inicialización al arrancar el servidor"""
    logger.info("🚀 Iniciando Jorge Aguirre Flores Web v2.0")
    
    # Inicializar base de datos
    if database.initialize():
        logger.info("✅ Base de datos PostgreSQL conectada")
    else:
        logger.info("ℹ️ Ejecutando sin base de datos")
    
    logger.info(f"📊 Meta Pixel ID: {settings.META_PIXEL_ID}")
    logger.info(f"🌐 Servidor listo en http://{settings.HOST}:{settings.PORT}")


@app.on_event("shutdown")
async def shutdown_event():
    """Limpieza al detener el servidor"""
    logger.info("🛑 Deteniendo servidor...")


# =================================================================
# ARRANQUE
# =================================================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True  # Hot reload para desarrollo
    )
