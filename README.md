# Jorge Aguirre Flores | Arte Facial & Microblading

![Status](https://img.shields.io/badge/Status-Elite%20Production-gold?style=for-the-badge)
![Security](https://img.shields.io/badge/Security-Rate%20Limited-blue?style=for-the-badge&logo=shield)
![CI/CD](https://img.shields.io/badge/Build-Passing-green?style=for-the-badge&logo=github-actions)
![Docker](https://img.shields.io/badge/Docker-Multi--Stage-blue?style=for-the-badge&logo=docker)

## 🌟 Visión General

> **Valoración Técnica:** $3,500 USD (Elite Standard)

Este proyecto es una plataforma web de alto rendimiento para **Jorge Aguirre Flores**, optimizada para conversión (CRO), SEO local y escalabilidad técnica. Implementa una arquitectura **Server-Side Tracking (CAPI)** y un pipeline de **CI/CD** automatizado.

## 🌟 Características Principales

### 🎨 UX/UI de Lujo (High-End)
- **Diseño Glassmorphism**: Paneles translúcidos y degradados dorados acelerados por hardware.
- **Micro-interacciones**: Animaciones suaves con `GSAP` y `Lenis` (Smooth Scroll), optimizadas para móviles.
- **Galería Interactiva**: Sliders "Antes/Después" con soporte táctil nativo y `clip-path` CSS para máximo rendimiento.
- **Tipografía Responsiva**: Sistema de escala fluida para legibilidad perfecta en cualquier dispositivo.

### 🚀 Rendimiento y WPO (Web Performance Optimization)
- **Carga Condicional**: Scripts pesados (Lenis, Particles) solo cargan en escritorio.
- **Core Web Vitals**:
  - `loading="lazy"` native en imágenes below-the-fold.
  - `fetchpriority="high"` para el LCP (Hero Image).
  - Imágenes en formato **WebP** de última generación.
- **Battery Friendly**: Detección de `prefers-reduced-motion` para desactivar efectos costosos en dispositivos de bajo consumo.

### 🔍 SEO Local y Semántica
- **JSON-LD Schema**: Datos estructurados para `BeautySalon`, incluyendo geo-coordenadas y horarios.
- **SEO Semántico**: Jerarquía H1-H3 optimizada para keywords locales ("Microblading Santa Cruz").
- **Meta Tags**: Open Graph y Twitter Cards configurados para compartir en redes sociales.

---

## 🛠️ Stack Tecnológico

La arquitectura sigue un enfoque **monolítico moderno** para simplificar el despliegue y maximizar la velocidad de renderizado.

- **Backend**: Python 3.11 + FastAPI (Rendimiento asíncrono).
- **Frontend**: Jinja2 Templates + Vanilla JS (Sin frameworks pesados de cliente).
- **Estilos**: Tailwind CSS (Utility-first) + Custom CSS (`input.css`) para efectos específicos.
- **Infraestructura**: Docker Multi-stage build + Gunicorn/Uvicorn Workers.

---

## ⚡ Guía de Inicio Rápido (Docker-First)

Este proyecto utiliza **Docker** como entorno de desarrollo estándar para garantizar la paridad con producción y eliminar problemas de configuración local.

### Requisitos previos
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado y corriendo.

### 1. Clonar el repositorio
```bash
git clone https://github.com/SrAndres629/jorge-aguirre-web.git
cd jorge-aguirre-web
```

### 2. Configurar Variables
Crea el archivo `.env`:
```bash
cp .env.example .env
```

### 3. Iniciar Entorno de Desarrollo
Este comando construye el contenedor e inicia el servidor con **Hot-Reloading** activo.
```bash
docker-compose up --build
```
Visita `http://127.0.0.1:8000`

> **Nota**: Los cambios que hagas en `templates/` o `static/` se reflejarán automáticamente sin reiniciar el contenedor.

---

## 🐢 Desarrollo Legacy (Manual)

Si no puedes usar Docker, puedes ejecutarlo manualmente desde `/core`:

```bash
cd core
python -m venv venv
.\venv\Scripts\activate  # Windows
# o: source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
uvicorn main:app --reload
```

Visita `http://localhost:8000`

---

## 🐳 Docker Deployment

El proyecto incluye un `Dockerfile` optimizado para producción.

### Build & Run
```bash
docker build -t jorge-web .
docker run -d -p 80:80 --name jorge-app jorge-web
```

---

## ☁️ Despliegue en Render

La configuración está automatizada mediante `render.yaml`.

1. Conecta tu repositorio de GitHub a Render.
2. Render detectará automáticamente el archivo `render.yaml`.
3. **Producción Ready**: Usa `gunicorn` con 4 workers (definido en `render.yaml` y `Procfile`) para robustez.

**Variables de Entorno (Producción):**
- `PYTHON_VERSION`: `3.11.0`
- `PORT`: `10000` (Automático en Render)

---

## 📂 Estructura del Proyecto

> **Nueva Arquitectura Profesional** (2026-01-06)  
> El proyecto ha sido reestructurado para separar código de producción de activos de desarrollo.  
> Ver [STRUCTURE.md](./STRUCTURE.md) para documentación completa.

```text
/jorge-aguirre-web
├── core/                   # 🚀 CÓDIGO DE PRODUCCIÓN
│   ├── app/               # Lógica de negocio Python
│   │   ├── routes/        # Endpoints FastAPI
│   │   ├── config.py      # Configuración
│   │   ├── database.py    # Conexión Supabase
│   │   ├── models.py      # Schemas Pydantic
│   │   └── tracking.py    # Meta CAPI
│   ├── static/            # Assets (CSS, JS, Imágenes)
│   ├── templates/         # HTML Jinja2
│   ├── main.py           # Entry point
│   ├── requirements.txt  # Dependencias
│   ├── Dockerfile        # Build production
│   └── Procfile          # Comando Render
│
├── database/              # 📊 Scripts SQL
│   └── migrations/       # Migraciones
│
├── automation/            # 🤖 Workflows n8n
│   └── workflows_json/   # Exportaciones JSON
│
├── scripts/               # 🔧 Utilidades
│   ├── maintenance/      # Scripts de mantenimiento
│   └── utils/            # Herramientas de desarrollo
│
├── docs/                  # 📚 Documentación
│   └── audits/           # Reportes de rendimiento
│
├── .env.example          # Plantilla de variables
├── .gitignore            # Seguridad (enterprise-grade)
├── STRUCTURE.md          # Documentación de arquitectura
└── docker-compose.yml    # Orquestación local
```

---

## 🔄 Git Workflow (Protocolo Jorge Aguirre)

Este proyecto sigue una **estrategia de ramas** para garantizar que el código en producción esté auditado.

### Ramas Principales

| Rama | Propósito | Conectada a Render |
|------|-----------|-------------------|
| `main` | **Producción** - Solo código auditado | ✅ SÍ |
| `develop` | **Desarrollo** - Trabajo diario | ❌ NO |

### Workflow de Desarrollo

1. **Trabajar en `develop`**:
   ```bash
   git checkout develop
   git add .
   git commit -m "feat: nueva funcionalidad"
   git push origin develop
   ```

2. **Después de pasar Auditoría (Fase 2B del Protocolo)**:
   ```bash
   git checkout main
   git merge develop
   git push origin main  # ✅ Render se actualiza automáticamente
   ```

3. **Volver a desarrollo**:
   ```bash
   git checkout develop
   ```

---

## ☁️ Configuración de Render

### Settings Requeridos

1. **Branch**: `main`
2. **Root Directory**: `core` ← **CRÍTICO: Apunta solo al código de producción**
3. **Build Command**: `pip install -r requirements.txt`
4. **Start Command**: (Auto-detectado desde `Procfile`)

### Variables de Entorno (Render Dashboard)

Configura estas variables en **Render → Settings → Environment**:

```bash
# Base de datos
DATABASE_URL=postgresql://...

# Meta Marketing API
META_PIXEL_ID=your_pixel_id
META_ACCESS_TOKEN=your_token

# WhatsApp (Evolution API)
EVOLUTION_API_URL=https://...
EVOLUTION_API_KEY=your_key

# n8n Automation
N8N_WEBHOOK_URL=https://...
```

> Ver `.env.example` para la lista completa de variables.

---

---

## 📝 Licencia

Este proyecto es propiedad de **Jorge Aguirre Flores**. Todos los derechos reservados.
Desarrollado con ❤️ y ☕ por el equipo de ingeniería.
