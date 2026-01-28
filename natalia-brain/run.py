import uvicorn
import os
import sys

# Agregar el directorio actual al path para que Python encuentre los módulos
# Esto asegura que "app.main" se resuelva correctamente desde la raíz
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    print(f"🚀 Starting Natalia Brain on port {port}...")
    
    # Importar app aquí para atrapar errores antes de que Uvicorn tome el control
    try:
        from app.main import app
        print("✅ App imported successfully.")
    except Exception as e:
        print(f"❌ CRITICAL ERROR importing app: {e}")
        # Crear una app dummy de emergencia para que el contenedor NO muera
        from fastapi import FastAPI
        from fastapi.responses import JSONResponse
        app = FastAPI()
        @app.get("/")
        @app.get("/health")
        def crash_report():
            return JSONResponse(
                status_code=500,
                content={
                    "status": "crashed", 
                    "error": str(e),
                    "message": "Revise los logs de Render para ver el traceback completo."
                }
            )

    # Iniciar servidor
    # Usamos "app.main:app" si importó bien, o el objeto 'app' directo si estamos en modo crash
    uvicorn.run(app, host="0.0.0.0", port=port)
