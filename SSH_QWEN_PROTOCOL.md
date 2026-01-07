# 🧠 PROTOCOLO DE CONEXIÓN SSH/QWEN (The Heavy Lifter)

## Objetivo
Establecer un canal seguro para que los agentes "ligeros" (Antigravity/Gemini) deleguen tareas complejas de refactorización y edición masiva al agente "pesado" (Qwen) que reside en el contenedor `antigravity_brain`.

## Datos de Conexión
*   **Host:** `localhost`
*   **Puerto:** `2222`
*   **Usuario:** `root` (o usuario configurado en Dockerfile)
*   **Modelo:** `ollama/qwen2.5-coder:7b` (Ejecutándose localmente en el contenedor)

## Flujo de Delegación
Cuando el Agente de Desarrollo (Fase Roja) enfrenta una tarea que requiere entender múltiples archivos o refactorizar una estructura completa:

1.  **Conexión:** Se conecta vía SSH al contenedor.
    ```bash
    ssh -p 2222 root@localhost
    ```
2.  **Contexto:** Navega al volumen montado `/app`.
3.  **Ejecución:** Invoca a `aider` o scripts de Python pesados.
    ```bash
    aider --model ollama/qwen2.5-coder:7b --message "Refactoriza core/app/database.py para usar Singleton"
    ```
4.  **Confirmación:** Verifica el resultado y cierra la sesión.

## Persistencia
Todo lo que sucede dentro de `/app` en el contenedor se refleja inmediatamente en el sistema de archivos del host (Windows), asegurando que la memoria del proyecto se mantenga intacta.

## Comandos de Mantenimiento
*   **Reiniciar Cerebro:** `docker restart antigravity_brain`
*   **Ver Logs:** `docker logs antigravity_brain`
