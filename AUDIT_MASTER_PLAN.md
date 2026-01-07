# 🏛️ AUDIT MASTER PLAN: Protocolo de Relevo

**Objetivo**: Orquestación de la "Gran Auditoría Autónoma" entre Gemini, Antigravity y Qwen.

## ROLES
1.  **GEMINI (Auditor Jefe)**: Análisis lógico y seguridad.
2.  **QWEN/ANTIGRAVITY (Ejecutor)**: Edición de código (Aider/Docker).
3.  **ANTIGRAVITY (IDE)**: Contexto y disparador.

## 🔄 FLUJO DE TRABAJO

### PASO 1: Generar Contexto
El Agente IDE genera una "foto" del código en `PROJECT_CONTEXT.txt`.

### PASO 2: La Auditoría (Gemini)
Gemini lee el contexto y crea una lista de tareas en `AUDIT_PLAN.md`.
*Formato:* `[ ] TAREA: [Archivo] - [Instrucción]`

### PASO 3: La Ejecución (Qwen)
Qwen lee el plan y usa Aider para aplicar cambios.
*Comando:*
```bash
docker exec antigravity_brain aider \
  --model ollama/qwen2.5-coder:7b \
  --message "Implementa el plan en AUDIT_PLAN.md" \
  --yes
```

## 📂 ARTEFACTOS
- `PROJECT_CONTEXT.txt`: Estado actual.
- `AUDIT_PLAN.md`: Órdenes de Gemini.
- `AUDIT_REPORT_COMPLETED.md`: Reporte final.
