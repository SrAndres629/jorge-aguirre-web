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
│   ├── static/            # Assets estáticos (optimización en build)
│   └── templates/         # UI Components (Jinja2)
│
├── data/                  # 📊 PERSISTENCIA (Docker Volumes)
│
├── docs/                  # 📚 DOCUMENTACIÓN & AUDITORÍAS
│
├── archive/               # 📂 ARCHIVO (Logs y Auditorías históricas)
│
├── Dockerfile             # 🐳 BUILD PRODUCTION (Optimizado Multi-stage)
├── docker-compose.yml     # 🛠️ ORQUESTACIÓN LOCAL & DEV
├── render.yaml            # ☁️ BLUEPRINT DE DESPLIEGUE (Render.com)
```

---

## 🔄 Protocolo de Desarrollo "Jorge Aguirre"

Para mantener la integridad del sistema, seguimos este ciclo:
1. **Fase 1: Desarrollo**: Implementación funcional en `/core`.
2. **Fase 2: Auditoría**: Ejecutar `scripts/maintenance/audit_project_full.py`.
3. **Fase 3: Saneamiento**: Correr `cleanup.bat` para eliminar residuos temporales.
4. **Fase 4: Commit**: Realizar el "Golden Commit" solo cuando todos los checks están en verde.

---

## ☁️ Despliegue en Render

El proyecto está configurado para despliegue automático vía **Docker**.
1. **Zero-Config**: Render detectará el `Dockerfile` en el root automáticamente.
2. **Environment**: Configurar el archivo `.env` en el panel de Render o mediante `render.yaml`.
3. **Health Checks**: Endpoint `/health` expuesto en el puerto `8000`.
4. **Infrastructure as Code**: El archivo `render.yaml` sirve como blueprint para la infraestructura.

## 📝 Licencia

Este proyecto es propiedad de **Jorge Aguirre Flores**. Todos los derechos reservados.
Desarrollado con ❤️ por el equipo de ingeniería avanzada.
