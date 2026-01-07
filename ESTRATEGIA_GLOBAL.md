# 🧠 ESTRATEGIA GLOBAL: Sistema Autónomo "Jorge Aguirre"

## 1. Visión del Sistema
Este documento define la arquitectura de un sistema autónomo diseñado para operar, mantener y evolucionar la infraestructura digital de "Jorge Aguirre". El sistema no es una herramienta pasiva, sino un **organismo digital cooperativo** compuesto por tres agentes especializados que interactúan a través de protocolos estrictos.

## 2. Arquitectura de la Triada (Los Agentes)

El sistema se divide en tres roles funcionales. Cada rol es asumido por la IA (Gemini/Antigravity/Qwen) dependiendo del contexto de la tarea.

### 🔵 [Módulo 1: PLANIFICACIÓN (El Arquitecto)](./MODULO_PLANIFICACION.md)
*   **Responsabilidad:** Estrategia, análisis de requisitos, diseño de flujos y "Mundo Ideal".
*   **Herramientas:** `n8n-architect`, `mcp-memory`, Análisis de Logica.
*   **Output:** `implementation_plan.md`, Diagramas, Grafos de Decisión.

### 🔴 [Módulo 2: DESARROLLO (El Constructor)](./MODULO_DESARROLLO.md)
*   **Responsabilidad:** Escritura de código, integración de APIs, refactorización y ejecución técnica.
*   **Herramientas:** `aider`, `docker-exec`, `ssh`, Python, JS.
*   **Output:** Commits, Código Funcional, Contenedores Docker activos.

### 🟢 [Módulo 3: AUDITORÍA (El Guardián)](./MODULO_AUDITORIA_DESPLIEGUE.md)
*   **Responsabilidad:** Validación, seguridad, pruebas de humo, despliegue y "Realidad Actual".
*   **Herramientas:** `curl`, Pruebas unitarias, `sentry`, `logs`, Logs de Docker.
*   **Output:** `walkthrough.md`, Reportes de Estado, Aprobación de Despliegue.

## 3. Flujo de Trabajo (El Ciclo Vital)

Todas las tareas complejas deben seguir este ciclo:

1.  **Input:** Solicitud del Usuario o Disparador Automático (Alerta, Cron).
2.  **Fase Azul (Arquitecto):** Se analiza el impacto y se actualiza el `ESTRATEGIA_GLOBAL.md` si es necesario. Se crea un plan.
3.  **Fase Roja (Constructor):** Se escribe el código en iteraciones cortas. El agente `antigravity` (Qwen) puede ser invocado vía SSH para tareas pesadas.
4.  **Fase Verde (Guardián):** Se audita el código. Si falla, regresa a la Fase Roja. Si pasa, se marca como listo.
5.  **Memoria:** Se registran los logros y lecciones aprendidas en el sistema de memoria persistente.

## 4. Infraestructura Base

El sistema vive sobre una infraestructura Dockerizada:
-   **Cerebro:** `antigravity_brain` (Qwen + Aider + SSH).
-   **Nervios:** `n8n` (Orquestación de webhooks y lógica).
-   **Voz:** `evolution_api` (WhatsApp).
-   **Cuerpo:** `jorge-web` (FastAPI + React/Frontend).

## 5. Protocolo de Emergencia
Si un agente se bloquea o entra en bucle:
1.  El Guardián detecta la anomalía.
2.  Se notifica al Usuario vía WhatsApp (Evolution).
3.  Se revierte al último estado estable conocido (Git/Docker volume).
