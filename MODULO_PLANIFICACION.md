# MODULO_PLANIFICACION.md
## 🧠 Fase 1: Definición de Rutas y Datos

### 🎯 Objetivo
Diseñar la estructura de datos que permitirá a n8n recordar el contexto de un usuario de WhatsApp a través del tiempo, vinculándolo a su origen en Meta Ads.

### 📋 Capacidades Requeridas
* Análisis de JSON Schema.
* Diseño de Bases de Datos (Supabase/PostgreSQL recomendado para n8n).

### 📝 Órdenes para Agente ALPHA
1.  **Esquema de Base de Datos:**
    * Diseñar tabla `users`: ID, teléfono, nombre, origen (Meta Ad ID), estado_funnel.
    * Diseñar tabla `conversations`: ID, user_id, timestamp, mensaje, resumen_contextual (generado por AI).
2.  **Mapeo de Webhooks:**
    * Definir estructura del payload entrante de Evolution API (WhatsApp).
    * Definir estructura del payload entrante de Meta Ads (Lead Forms).
3.  **Lógica de Enrutamiento:**
    * Crear diagrama de flujo: Si `mensaje` contiene "precio" -> Trigger nodo AI -> Respuesta Venta.

### ✅ Validaciones y Entregables
* [ ] Archivo `schema.sql` creado en `/database`.
* [ ] Diagrama MermaidJS del flujo de n8n en `/docs/flow.mermaid`.
