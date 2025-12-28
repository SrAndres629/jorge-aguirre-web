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

Si no puedes usar Docker, puedes ejecutarlo manualmente (No recomendado):
1. `python -m venv venv`
2. `.\venv\Scripts\activate`
3. `pip install -r requirements.txt`
4. `uvicorn main:app --reload`

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

```text
.
├── app/
│   ├── routes/         # Endpoints (FastAPI)
│   ├── services/       # Lógica de negocio y configs
│   └── templates/      # (Legacy path, templates están en raíz)
├── static/
│   ├── css/            # CSS compilado (output.css)
│   ├── js/             # Lógica Frontend (ui.js, motion.js)
│   └── images/         # Assets optimizados (WebP)
├── templates/          # HTML Jinja2 (index.html, robots.txt)
├── Dockerfile          # Configuración de imagen Docker (Prod)
├── render.yaml         # Blueprint para Render.com
├── requirements.txt    # Dependencias Python
└── tailwind.config.js  # Configuración del Design System
```

---

## 📝 Licencia

Este proyecto es propiedad de **Jorge Aguirre Flores**. Todos los derechos reservados.
Desarrollado con ❤️ y ☕ por el equipo de ingeniería.
