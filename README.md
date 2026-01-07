# Jorge Aguirre Flores | Arte Facial & Microblading

![Status](https://img.shields.io/badge/Status-Elite%20Production-gold?style=for-the-badge)
![Security](https://img.shields.io/badge/Security-Hardened-green?style=for-the-badge&logo=shield)
![Architecture](https://img.shields.io/badge/Architecture-Modular%20%2F%20Lean-blue?style=for-the-badge)
![Docker](https://img.shields.io/badge/Docker-Multi--Service-blue?style=for-the-badge&logo=docker)

## 🌟 Visión General

Este proyecto es una plataforma web de alto rendimiento para **Jorge Aguirre Flores**, optimizada para conversión (CRO), SEO local y robustez técnica. Implementa una arquitectura modular con **Server-Side Tracking (CAPI)**, tareas en segundo plano mediante **Celery** y un sistema de configuración centralizado.

---

## 🛠️ Stack Tecnológico

- **Backend**: Python 3.11 + FastAPI (Asíncrono y modular).
- **Worker**: Celery + Redis (Procesamiento de eventos en background).
- **Frontend**: Jinja2 Templates + Vanilla JS + CSS Glassmorphism.
- **Base de Datos**: PostgreSQL (Supabase) con fallback local a SQLite.
- **Orquestación**: Docker Compose (Web, Worker, Redis, n8n, Evolution API).
- **Infraestructura**: Docker Multi-stage + Pydantic Settings.

---

## ⚡ Guía de Inicio Rápido (Docker-First)

El entorno recomendado es Docker para garantizar la paridad absoluta entre desarrollo y producción.

### 1. Clonar e Instalar
```bash
git clone https://github.com/SrAndres629/jorge-aguirre-web.git
cd jorge-aguirre-web
cp .env.example .env
```

### 2. Iniciar Ecosistema
Este comando inicia la web, el worker de Celery y todas las dependencias:
```bash
docker-compose up --build -d
```
- **Web App**: `http://localhost:8000`
- **n8n**: `http://localhost:5678`
- **Evolution API**: `http://localhost:8081`

---

## 🧩 Configuración (Pydantic Settings)

El sistema utiliza un Singleton de configuración centralizado en `core/app/config.py`.

### Validación de Entorno
Todas las variables se validan al inicio del servicio. Si falta una variable crítica (como `META_ACCESS_TOKEN`), el sistema emitirá warnings claros pero permitirá el inicio en modo limitado.

```python
from app.config import settings
print(settings.DATABASE_URL)
```

---

## 📂 Estructura del Proyecto (Clean Architecture)

```text
/jorge-aguirre-web
├── core/                   # 🚀 CÓDIGO DE PRODUCCIÓN (FastAPI Package)
│   ├── main.py            # Entry point de la aplicación FastAPI
│   ├── app/               # Lógica de negocio (routes, models, services)
│   ├── database/          # Persistencia Local & Migraciones
│   ├── static/            # Assets estáticos (optimización en build)
│   └── templates/         # UI Components (Jinja2)
│
├── automation/            # 🤖 AUTOMATIZACIÓN (n8n Workflows)
├── data/                  # 📊 PERSISTENCIA (Docker Volumes)
├── docs/                  # 📚 DOCUMENTACIÓN & AUDITORÍAS
├── infrastructure/        # 🏗️ INFRAESTRUCTURA (Dockerfiles supporting)
├── scripts/               # 📜 SCRIPTS DE MANTENIMIENTO
│
├── Dockerfile             # 🐳 BUILD PRODUCTION (Optimizado Multi-stage)
├── docker-compose.yml     # 🛠️ ORQUESTACIÓN LOCAL & DEV
├── render.yaml            # ☁️ BLUEPRINT DE DESPLIEGUE (Render.com)
├── PROJECT_STRUCTURE_MAP.md # 🗺️ MAPA TÉCNICO COMPLETO
└── RENDER_DEPLOY_FIX.md   # 🛠️ REPORTE DE DESPLIEGUE

---

## 🔄 Protocolo de Desarrollo "Jorge Aguirre"

Para mantener la integridad del sistema, seguimos este ciclo:
1. **Fase 1: Desarrollo**: Implementación funcional en `/core`.
2. **Fase 2: Auditoría**: Ejecutar `scripts/maintenance/audit_project_full.py`.
3. **Fase 3: Saneamiento**: Correr `cleanup.bat` para eliminar residuos temporales.
4. **Fase 4: Commit**: Realizar el "Golden Commit" solo cuando todos los checks están en verde.

---

## ☁️ Despliegue en Render (CRITICAL)

El proyecto está configurado para despliegue automático vía **Docker**. Para un despliegue exitoso, asegúrate de configurar estos campos en el Dashboard de Render (**Settings -> Build & Deploy**):

1. **Root Directory**: Déjalo **VACÍO** (Borra "core" si está presente).
2. **Dockerfile Path**: `Dockerfile`
3. **Docker Build Context Directory**: `.` (Un punto).

### 🛠️ Herramientas de Mantenimiento
- **`cleanup.sh`**: Ejecútalo para limpiar residuos antes de un commit.
- **`PROJECT_STRUCTURE_MAP.md`**: Consulta este mapa para entender la arquitectura detallada.
- **`RENDER_DEPLOY_FIX.md`**: Detalles técnicos de la última resolución de fallos.

## 📝 Licencia

Este proyecto es propiedad de **Jorge Aguirre Flores**. Todos los derechos reservados.
Desarrollado para mi amada Natalia. te amo mi vida. por el equipo de ingeniería avanzada.
