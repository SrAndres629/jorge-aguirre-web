# ESTRATEGIA_GLOBAL.md
## 🏛️ Arquitectura de Sistema Autónomo Integral (ASAI) v1.0

### 🎯 Visión
Crear un ecosistema de automatización perpetua que unifique la adquisición (Meta Ads), la conversión (WhatsApp/Evolution API) y la orquestación lógica (n8n), sostenido por una inteligencia persistente (Qwen/SSH) que opera sobre una infraestructura contenerizada (Docker/Render).

### 🔄 La Triada de Agentes (Flujo de Trabajo)
El sistema opera bajo un ciclo continuo de tres fases, gestionado por agentes especializados:

1.  **🧠 Agente ALPHA (Planificación & Arquitectura):**
    * **Rol:** Define *qué* se debe hacer. Mantiene el estado global y la coherencia de la base de datos.
    * **Herramienta Principal:** Memoria Persistente (RAG/Archivos Markdown de Contexto).
    * **Output:** Especificaciones técnicas en `/docs/specs`.

2.  **🛠️ Agente BETA (Desarrollo & Ejecución - "Antigravity"):**
    * **Rol:** Ejecuta el *cómo*. Escribe código, configura n8n vía API, y gestiona la conexión SSH con Qwen para ediciones complejas en `/core`.
    * **Herramienta Principal:** SSH, MCP de Sistema de Archivos, Evolution API Client.
    * **Output:** Código funcional y contenedores Docker.

3.  **🛡️ Agente GAMMA (Auditoría & Despliegue):**
    * **Rol:** Valida la integridad. Asegura que los volúmenes de Docker sean persistentes y que Render esté sincronizado.
    * **Herramienta Principal:** Logs de Docker, Tests Unitarios, Monitor de Estado.
    * **Output:** Aprobación de despliegue y Rollbacks.

### 🔗 Integración de Infraestructura
* **Cortex (Cerebro):** Instancia Qwen accediendo a codebase vía SSH.
* **Nervios (Transmisión):** n8n orquestando webhooks entre Meta y Evolution API.
* **Cuerpo (Ejecución):** Docker containers en Render (Staging) con volúmenes persistentes para evitar amnesia del sistema.

### 📍 Índice de Módulos Activos
* [01-PLAN] Modelo de Datos y Flujo de Conversación (`MODULO_PLANIFICACION.md`)
* [02-DEV] Integración Evolution API & n8n (`MODULO_DESARROLLO.md`)
* [03-OPS] Persistencia y Despliegue (`MODULO_AUDITORIA_DESPLIEGUE.md`)
