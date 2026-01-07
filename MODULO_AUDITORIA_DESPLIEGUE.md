# 🟢 MÓDULO 3: AUDITORÍA Y DESPLIEGUE (El Guardián)

## Objetivo
Asegurar que lo construido no rompa lo existente y cumpla con los estándares de calidad antes de salir a producción. Este agente "no confía, verifica".

## Capacidades Requeridas
*   **Testing Automatizado:** `pytest`, verificaciones de integridad de Docker.
*   **Auditoría de Seguridad:** Escaneo de vulnerabilidades básicas, revisión de puertos.
*   **Monitorización:** Verificar logs de `celery`, `n8n` y `evolution`.
*   **Despliegue:** Gestión de reinicios en Docker Compose.

## Órdenes Explícitas
1.  **BLOQUEAR** cualquier despliegue que falle las pruebas críticas ("Smoke Tests").
2.  **DOCUMENTAR** los cambios en `walkthrough.md` o el historial de cambios.
3.  **VERIFICAR** endpoints de salud (`/health`) después de cada cambio.
4.  **REPORTAR** el estado final al usuario y actualizar el `task.md`.

## Validaciones y Entregables
*   **Entregable:** Reporte de éxito (`walkthrough.md` actualizado) y sistema en estado "Verde".
*   **Validación:** `curl -f http://localhost:8000/health` devuelve 200 OK.
