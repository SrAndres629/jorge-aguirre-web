# MODULO_DESARROLLO.md
## Operador $\beta$: Construcción y Ejecución (The Constructor)

### 1. Definición Funcional
Sea $\beta$ un operador de transformación que aplica la especificación $\mathcal{T}$ sobre el sustrato físico $\mathcal{I}$ (Código/Infraestructura).
$$ \beta: \mathcal{T} \times \mathcal{I}_t \rightarrow \mathcal{I}_{t+1} $$

### 2. Mecánica de Interacción (SSH Tunneling)
El operador $\beta$ posee privilegios de acceso al Núcleo Computacional (Cortex / `antigravity_brain`).
*   **Protocolo:** $\text{SSH}(u, h, p)$ donde $p=2222$.
*   **Acción:** `exec(script)` sobre el volumen persistente $/app$.

### 3. Algoritmo de Implementación
Para ejecutar una tarea $k$:
1.  **Inicialización:** Instanciar el entorno $\mathbb{E}_{dev}$ (Docker Container).
2.  **Conexión:** Establecer enlace con Evolution API ($V$).
    *   $\text{Hook}(V) \rightarrow W_{n8n}$ (Webhook Binding).
3.  **Codificación:** Generar/Refactorizar código fuente $C$.
    *   Si $C$ es complejo $\implies$ invocar Qwen vía SSH.
4.  **Integración:** Inyectar dependencias $\mathcal{D}$ en el contenedor.

### 4. Funciones Críticas
*   `RestoreSession()`: Función idempotente que garantiza la conectividad de $V$ si $\text{Status}(V) \neq \text{ONLINE}$.
*   `MemoryRead()`: Leer historial $H$ de la DB antes de inferencia.

### ✅ Vector de Validación
*   [ ] $\text{ExitCode}(\text{Build}) == 0$.
*   [ ] $\text{Ping}(\text{EvolutionAPI}) < 100ms$.
*   [ ] $\exists$ flujo de datos bidireccional $User \leftrightarrow System$.
