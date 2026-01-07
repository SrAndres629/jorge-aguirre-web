# MODULO_DESARROLLO.md
## 🛠️ Fase 2: Construcción e Integración (Código Puro)

### 🎯 Objetivo
Implementar los scripts de conexión y los workflows de n8n, asegurando que Qwen pueda editar el código base vía SSH sin romper la producción.

### 📋 Capacidades Requeridas
* Acceso SSH al servidor de desarrollo.
* Manejo de Dockerfiles.
* Conocimiento de Evolution API v2.

### 📝 Órdenes para Agente BETA (Antigravity)
1.  **Configuración de Evolution API:**
    * Generar script en Python/Node para instanciar una nueva sesión de WhatsApp automáticamente si se cae.
    * Configurar Webhook global en Evolution API apuntando al endpoint de n8n.
2.  **Workflows de n8n (JSON):**
    * Importar el JSON del workflow base que conecta `Webhook (Evo)` -> `HTTP Request (Qwen/LLM)` -> `HTTP Request (Evo Send)`.
3.  **Persistencia de Memoria:**
    * Implementar script que lea el historial de chat de la DB antes de enviar el prompt a Qwen.

### ✅ Validaciones y Entregables
* [ ] `docker-compose.yml` configurado con servicios n8n, db y evo-api (o puente a evo externa).
* [ ] Script `restore_session.py` funcional.
* [ ] Test de envío/recepción de mensaje exitoso.
