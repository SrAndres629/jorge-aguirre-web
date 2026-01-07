# MODULO_PLANIFICACION.md
## Operador $\alpha$: Arquitectura y Especificación (The Architect)

### 1. Definición Funcional
Sea $\alpha$ un operador que mapea el espacio de Intenciones del Usuario ($\mathcal{U}$) al espacio de Especificaciones Técnicas ($\mathcal{T}$).
$$ \alpha: \mathcal{U} \rightarrow \mathcal{T} $$

### 2. Parámetros del Estado Objetivo
El operador $\alpha$ es responsable de minimizar la ambigüedad $\epsilon$ en la definición del sistema.

#### Función de Mapeo de Datos $\Psi_{data}$
El objetivo es establecer una biyección entre la identidad del usuario en Meta Ads ($u_{meta}$) y su sesión en WhatsApp ($u_{wa}$).
*   **Entidad:** `User`
*   **Métrica:** $u_{id} \in \mathbb{R}^+$
*   **Tupla:** $\langle u_{wa}, u_{meta}, \text{timestamp}, \text{context\_vector} \rangle$

#### Función de Topología de Flujo $\Phi_{flow}$
Definir el grafo dirigido acíclico (DAG) para n8n:
$$ G = (V, E) $$
Donde $V$ son los nodos de procesamiento (Webhooks, AI, Filter) y $E$ son las aristas de datos JSON.

### 3. Protocolo de Ejecución
Para toda nueva solicitud $req \in \mathcal{U}$:
1.  **Análisis:** Descomponer $req$ en primitivas atómicas.
2.  **Síntesis:** Construir el esquema $\mathcal{S}$ (SQL/JSON).
3.  **Persistencia:** Escribir $\mathcal{S}$ en el vector de memoria `/docs/specs`.

### 4. Invariantes (Reglas Absolutas)
*   $\forall x \in \text{Output}(\alpha)$: $x$ debe ser determinista.
*   $\nexists$ alucinación en el esquema de base de datos.
*   El diseño debe satisfacer $O(1)$ para la recuperación de contexto en tiempo real.

### ✅ Vector de Validación
*   [ ] $\exists$ `schema.sql` tal que `Validate(schema) == True`.
*   [ ] $G_{n8n}$ es conexo y libre de ciclos infinitos.
