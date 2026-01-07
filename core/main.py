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
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import ORJSONResponse
from fastapi.middleware.gzip import GZipMiddleware
import uvicorn
import logging
import gc

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
# EVENTOS DE CICLO DE VIDA
# =================================================================

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ciclo de vida de la aplicación con manejo de contexto"""
    # Startup
    logger.info("🚀 Iniciando Jorge Aguirre Flores Web v2.0")
    
    # Inicializar base de datos
    if database.initialize():
        logger.info("✅ Base de datos PostgreSQL conectada")
    else:
        logger.info("ℹ️ Ejecutando sin base de datos")
    
    logger.info(f"📊 Meta Pixel ID: {settings.META_PIXEL_ID}")
    logger.info(f"🌐 Servidor listo en http://{settings.HOST}:{settings.PORT}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Deteniendo servidor...")
    gc.collect()  # Force garbage collection on shutdown


# =================================================================
# APLICACIÓN FASTAPI
# =================================================================

app = FastAPI(
    title="Jorge Aguirre Flores Web",
    description="Sitio web profesional con tracking Meta CAPI",
    version="2.0.0",
    default_response_class=ORJSONResponse,
    lifespan=lifespan
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
        "https://jorge-aguirre-web.onrender.com",
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
# ARCHIVOS ESTÁTICOS
# =================================================================

# Montar archivos estáticos (Standard StaticFiles - Render should handle caching/CDN)
app.mount("/static", StaticFiles(directory="static"), name="static")


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
# EVENTOS DE CICLO DE VIDA (Movido arriba para lifespan)
# =================================================================



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
