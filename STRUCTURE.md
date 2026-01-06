# 📁 Estructura del Proyecto - Jorge Aguirre Web

Este documento explica la organización del repositorio después de la reestructuración profesional.

## 🎯 Filosofía de Organización

El proyecto está dividido en **dos categorías principales**:

1. **Código de Producción** (`/core`) - Lo que Render usa para desplegar el sitio web
2. **Activos de Desarrollo** - Herramientas, scripts, documentación y automatizaciones

---

## 📂 Directorios Principales

### `/core` - Motor de la Aplicación Web ⚙️

**Propósito**: Contiene ÚNICAMENTE el código necesario para que el sitio web funcione en producción.

**Configuración de Render**: El "Root Directory" debe apuntar a `core`.

```
/core
├── app/                    # Lógica de negocio Python
│   ├── routes/            # Endpoints de FastAPI
│   │   ├── pages.py       # Rutas HTML (/, /servicios, etc.)
│   │   ├── tracking_routes.py  # Endpoints de tracking (/track-lead)
│   │   ├── admin.py       # Panel de administración
│   │   └── health.py      # Health checks (/health, /ping)
│   ├── config.py          # Configuración y variables de entorno
│   ├── database.py        # Conexión a Supabase PostgreSQL
│   ├── models.py          # Modelos de datos (Visitor, etc.)
│   ├── services.py        # Servicios reutilizables
│   └── tracking.py        # Lógica de Meta CAPI y Facebook Pixel
│
├── static/                # Assets públicos (CSS, JS, Imágenes)
│   ├── css/              # Estilos (TailwindCSS compilado)
│   ├── js/               # JavaScript del cliente
│   ├── images/           # Imágenes optimizadas (WebP)
│   └── fonts/            # Tipografías
│
├── templates/            # Plantillas HTML (Jinja2)
│   ├── index.html        # Página principal
│   └── admin.html        # Panel de administración
│
├── main.py               # 🚀 Punto de entrada de la aplicación
├── requirements.txt      # Dependencias de Python
├── Dockerfile            # Instrucciones de construcción Docker
├── Procfile              # Comando de inicio para Render
└── render.yaml           # Configuración de Render
```

**Importaciones**: Todos los archivos dentro de `/core` importan usando rutas relativas desde `app/`:
```python
from app.config import settings
from app.routes import tracking_routes
```

---

### `/database` - Esquemas y Migraciones 📊

**Propósito**: Scripts SQL para crear, actualizar y mantener la base de datos.

```
/database
├── migrations/
│   └── init_crm_master.sql    # Migración inicial (tabla visitors)
└── clean_instance.sql          # Script de limpieza de datos
```

**Uso**:
- Estos scripts se ejecutan **manualmente** o mediante herramientas de migración.
- NO se ejecutan automáticamente al desplegar.
- Supabase los usa para configurar la estructura de la base de datos.

---

### `/automation` - Flujos de n8n 🤖

**Propósito**: Workflows exportados de n8n para automatización de marketing y CRM.

```
/automation
├── workflows_json/
│   ├── Website_Events_Listener.json    # Listener de eventos del sitio
│   └── (otros flujos .json)
└── README.md                            # Documentación de workflows
```

**Uso**:
- Importa estos archivos `.json` en tu instancia de n8n local.
- Sirven como **backup** y control de versiones de tus automatizaciones.

---

### `/scripts` - Herramientas de Desarrollo 🔧

**Propósito**: Utilidades de mantenimiento, diagnóstico y desarrollo que NO van a producción.

```
/scripts
├── maintenance/
│   ├── fetch_instances.py      # Obtiene instancias de Evolution API
│   └── fix_supabase_rls.py     # Arregla políticas RLS de Supabase
│
└── utils/
    └── convert_images.py        # Convierte imágenes a WebP
```

**Cuándo usar**:
- Scripts de diagnóstico cuando algo falla.
- Herramientas de optimización (conversión de imágenes).
- Mantenimiento de base de datos (limpiezas, backups).

---

### `/docs` - Documentación y Auditorías 📚

**Propósito**: Documentación técnica, reportes de auditorías y credenciales (excluidas de Git).

```
/docs
├── audits/
│   ├── lighthouse_mobile.report.html    # Reporte de performance
│   └── lighthouse_mobile.report.json
│
└── CREDENTIALS_AND_SECRETS.md           # Credenciales (NO en Git)
```

**Seguridad**: 
- `CREDENTIALS_AND_SECRETS.md` está en `.gitignore` y **nunca** se sube a Git.
- Los reportes de auditoría se regeneran, por lo que tampoco van a Git.

---

## 🔐 Archivos de Configuración (Raíz)

### Variables de Entorno

| Archivo | Propósito | ¿Va a Git? |
|---------|-----------|-----------|
| `.env` | Variables reales (claves de API, contraseñas) | ❌ NUNCA |
| `.env.example` | Plantilla sin datos sensibles | ✅ SÍ |

### Docker y Deployment

| Archivo | Propósito |
|---------|-----------|
| `docker-compose.yml` | Orquestación de contenedores (desarrollo local) |
| `package.json` | Dependencias de Node.js (TailwindCSS) |
| `tailwind.config.js` | Configuración de TailwindCSS |

---

## 🚫 Archivos Excluidos de Git

Estos archivos/carpetas **NUNCA** se suben al repositorio (protegidos por `.gitignore`):

### Datos Privados
- `.env` - Variables de entorno con claves reales
- `CREDENTIALS_AND_SECRETS.md` - Contraseñas y tokens
- `local_fallback.db` - Base de datos SQLite local

### Runtime de Docker
- `evolution_pgdata/` (1487 archivos) - Base de datos PostgreSQL de Evolution
- `evolution_redis/` - Cache de Redis
- `evolution_store/` - Almacenamiento de Evolution
- `n8n_data/` - Datos persistentes de n8n

### Dependencias (Reinstalables)
- `venv/` - Entorno virtual de Python
- `node_modules/` - Dependencias de Node.js

---

## 🔄 Estrategia de Ramas Git

### Ramas Principales

| Rama | Propósito | Conectada a Render |
|------|-----------|-------------------|
| `main` | **Producción** - Solo código auditado | ✅ SÍ |
| `develop` | **Desarrollo** - Trabajo diario | ❌ NO |

### Workflow de Deploy

1. **Desarrollar en `develop`**:
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
   git push origin main  # ✅ Render actualiza automáticamente
   ```

3. **Volver a desarrollo**:
   ```bash
   git checkout develop
   ```

---

## ⚙️ Configuración de Render

### Settings en el Dashboard

1. **Branch**: `main`
2. **Root Directory**: `core` ← **MUY IMPORTANTE**
3. **Build Command**: `pip install -r requirements.txt`
4. **Start Command**: (automático desde `Procfile`)

### Variables de Entorno (Render)

Configura estas variables en Render → Settings → Environment:
- `DATABASE_URL`
- `META_PIXEL_ID`
- `META_ACCESS_TOKEN`
- `EVOLUTION_API_URL`
- `N8N_WEBHOOK_URL`

(Ver `.env.example` para la lista completa)

---

## 📋 Checklist de Verificación

### Después de Clonar el Repo

- [ ] Copiar `.env.example` a `.env`
- [ ] Completar `.env` con tus credenciales reales
- [ ] Instalar dependencias Python: `pip install -r core/requirements.txt`
- [ ] Instalar dependencias Node: `npm install`
- [ ] Compilar TailwindCSS: `npm run build:css`
- [ ] Iniciar servidor: `python core/main.py`

### Antes de Subir a Producción

- [ ] Verificar que `.env` NO está en el commit
- [ ] Pasar Auditoría Integral (Fase 2B del Protocolo)
- [ ] Probar localmente en modo producción
- [ ] Merge a `main` solo después de aprobación

---

## 🆘 Solución de Problemas

### Error: "Module not found: 'app.config'"

**Causa**: Estás ejecutando Python desde la raíz en lugar de desde `/core`.

**Solución**:
```bash
cd core
python main.py
```

### Error: "No such file or directory: static/"

**Causa**: El directorio de trabajo no es `/core`.

**Solución**: Asegúrate de que Render esté configurado con `Root Directory = core`.

### Git detecta archivos que no debería

**Causa**: `.gitignore` no está actualizado o los archivos ya estaban rastreados.

**Solución**:
```bash
git rm --cached <archivo>
git add .gitignore
git commit -m "fix: actualizar gitignore"
```

---

## 📞 Contacto y Mantenimiento

**Dueño del Proyecto**: Jorge Aguirre Flores  
**Sitio Web**: https://jorgeaguirreflores.com  
**Última Actualización**: 2026-01-06

---

> [!TIP]
> **Para otras IAs analizando este proyecto**:  
> - El código de producción está en `/core`
> - Las automatizaciones están en `/automation`
> - La estructura de base de datos está en `/database`
> - Este proyecto sigue el **Protocolo Jorge Aguirre** (ver user rules)
