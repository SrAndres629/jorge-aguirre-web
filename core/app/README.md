# 🧠 CORE MEMORY: Backend Logic

**Dominio**: `Qwen/Local` (Acceso Verde y Amarillo)

## 🏗️ Arquitectura
- **Framework**: FastAPI (Asíncrono).
- **Entrada**: `main.py` (Singleton App Factory).
- **Configuración**: `config.py` (Pydantic Settings - solo lectura).

## 📂 Mapa de Rutas
- `routes/`: Endpoints modulares (APIRouter).
- `models.py`: Modelos de datos (SQLAlchemy / Pydantic).
- `services.py`: Lógica de negocio pura (reutilizable).

## 📝 Notas para Agentes
1.  **Tests**: Siempre correr `pytest` después de modificar `services.py`.
2.  **DB**: Usar `database.py` para sesiones. No crear conexiones manuales.
