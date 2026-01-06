# README - Automation Workflows

Este directorio contiene los flujos de trabajo (workflows) de n8n exportados como JSON.

## 📁 Contenido

- `Website_Events_Listener.json` - Listener principal de eventos del sitio web

## 🔄 Cómo Usar

### Importar en n8n

1. Abre tu instancia de n8n (http://localhost:5678)
2. Ve a **Workflows** → **Import from File**
3. Selecciona el archivo `.json` que deseas importar
4. Activa el workflow

### Exportar workflows (Backup)

1. Abre el workflow en n8n
2. Click en el menú **...** → **Download**
3. Guarda el archivo `.json` en este directorio
4. Commit los cambios a Git para control de versiones

## 🔐 Seguridad

Los archivos JSON **NO deben contener credenciales**. n8n las maneja por separado en su sistema de Credentials.

Si encuentras credenciales hardcodeadas en un JSON exportado, elimínalas antes de subir a Git.

## 📝 Documentación

Para cada workflow, documenta:
- **Propósito**: Qué automatiza
- **Trigger**: Qué lo activa (webhook, schedule, etc.)
- **Dependencias**: Qué servicios externos usa (Supabase, Meta API, WhatsApp)
