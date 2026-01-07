# 🧠 CAPACIDADES Y ÓRDENES: Protocolo de Inteligencia Distribuida

**SISTEMA DE MANDO CENTRAL**: Jorge Aguirre Web Architecture
**ESTADO**: Activo
**FECHA DE VIGENCIA**: 2026-01-07

---

## 1. 🛡️ La Triada de Inteligencia

Este sistema opera bajo una arquitectura de "Tres Cerebros", cada uno con un dominio específico. El objetivo es mantener una coherencia absoluta entre la estrategia en la nube y la ejecución local.

| Agente | Rol | Dominio | Herramienta Clave |
| :--- | :--- | :--- | :--- |
| **ANTIGRAVITY** | **Arquitecto de Nube** | Estrategia Global, Infraestructura, CI/CD, Diseño de APIs. | `Mente Maestra` |
| **QWEN 2.5** | **Ingeniero Local** | Ejecución Táctica, Refactorización, Tests Unitarios, Lógica Privada. | `Ollama` + `Docker` |
| **GEMINI CLI** | **Auditor de Contexto** | Análisis de Logs Masivos, Auditoría de Seguridad, Diagnóstico. | `Gemini Terminal` |

---

## 2. 📜 Protocolos de Mando

### 2.1. Protocolo de Planificación (Antigravity)
**Responsabilidad**: Definir el "Qué" y el "Por qué".
- **Orden**: Antes de cualquier código, se debe actualizar `task.md` e `implementation_plan.md`.
- **Salida**: Un plan aprobado por el usuario que sirve como "Fuente de Verdad" para Qwen.

### 2.2. Protocolo de Ejecución (Qwen/Local)
**Responsabilidad**: Ejecutar el "Cómo" (Coding).
- **Entrada**: Recibe instrucciones precisas derivadas del plan de Antigravity o comandos directos vía SSH.
- **Acceso SSH**: Habilitado para `Antigravity` y `n8n` en el puerto `2222`.
- **Acción**: Edita archivos, corre tests locales, optimiza funciones.
- **Restricción**: No toca configuración de despliegue (`render.yaml`, `Dockerfile`) sin permiso explícito.

### 2.3. Protocolo de Auditoría (Gemini CLI)
**Responsabilidad**: Verificar la Calidad y Seguridad.
- **Acción**: Escanea el repositorio completo antes de un "Golden Commit".
- **Comando**: `gemini analyze logs` o `gemini audit security`.
- **Meta**: Detectar patrones de error invisibles para el ojo humano o agentes limitados por contexto.

---

## 3. 🚦 Zonas de Operación

- **🟢 Zona Verde (Libre para Qwen)**: `core/app/`, `core/templates/`, `core/static/`.
- **🟡 Zona Amarilla (Supervisión Requerida)**: `automation/`, `core/database/migrations/`.
- **🔴 Zona Roja (Solo Antigravity)**: `infrastructure/`, `render.yaml`, `Dockerfile`, `.env`.

---

## 4. 🔄 Sincronización de Memoria

Para mantener la coherencia:
1. **Lectura**: Todos los agentes deben leer `PROJECT_STRUCTURE_MAP.md` antes de actuar.
2. **Escritura**: Solo Antigravity actualiza los archivos de "Brain Artifacts" (`brain/`).
3. **Persistencia**: El conocimiento local se documenta en los `README.md` de cada módulo (`Granular Memory`).

---
*Este documento es la Ley Suprema de Operación Técnica del Proyecto.*
