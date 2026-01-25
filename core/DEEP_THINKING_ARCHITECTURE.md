# Deep Thinking Architecture: specialized Web Design & Ads Integration

## 1. Core Philosophy: The Hexagon of Competence & Context Preservation
To avoid "Context Saturation" (where an AI tries to do everything and fails at specific details), we implement a **Federated Intelligence Model**.
-   **Single Responsibility**: Each "Skill" is an isolated expert context.
-   **Master Orchestration**: A central "Brain" that does not write code but directs those who do.
-   **Debt-Free Output**: Code is only generated after a full architectural thought process.

## 2. Universal "Full Stack" Cognitive Protocol (The Thought Chain)
*Every* skill, before outputting a single character of code, must strictly process the request through this 4-step loop:

### Phase 1: Architecture & Feasibility Audit
-   **Query**: "If I build this, what breaks?"
-   **Checklist**:
    -   Database Schema impact (Foreign keys, migrations needed?).
    -   API Latency & Limits (Meta Graph API rate limits?).
    -   Security Verification (SQL Injection, XSS, CSRF).
    -   Library Compatibility (conflicts with existing requirements.txt?).

### Phase 2: Data Flow Mapping
-   **Query**: "Trace the electron."
-   **Action**: Map the exact journey of data.
    -   `User Input` -> `Frontend Validation` -> `API Request` -> `Backend Middleware` -> `DB Query` -> `Response`.
    -   *Crucial for Ads*: `Event Trigger` -> `Browser Pixel` -> `Server-Side Event` -> `Deduplication ID` -> `Meta/Google Cloud`.

### Phase 3: Component & Module Design
-   **Query**: "Make it Atomic."
-   **Action**:
    -   Define exact directory structure.
    -   Define Types/Interfaces (Strict Typing).
    -   Identify reusable utilities vs. specific logic.

### Phase 4: Production-Ready Implementation
-   **Query**: "Is this Senior Level?"
-   **Checklist**:
    -   Error Handling (Try/Except blocks, Logging).
    -   Performance (Memoization, Indexing).
    -   Clean Code (Docstrings, meaningful variable names).
    -   *NO PLACEHOLDERS*.

---

## 3. Skill & Role Definitions (The "Agent" Manifestos)

### 3.1. MASTER ORCHESTRATOR ("The Architect")
-   **Filename**: `core/protocols/MASTER_ORCHESTRATOR.md`
-   **Mission**: High-level project state management.
-   **Powers**:
    -   Can invoke any Sub-Skill.
    -   Maintains the `task.md` and `project_state.json`.
    -   Rejects code that doesn't meet the "Senior" standard.
-   **Cognitive Focus**: Timelines, dependencies, feature completeness.

### 3.2. UX/UI VISIONARY ("The Artist")
-   **Filename**: `core/protocols/UX_UI_VISIONARY.md`
-   **Mission**: Create "Premium" visual experiences.
-   **Cognitive Focus**:
    -   Color Theory (HSL harmonies).
    -   Animation Physics (GSAP/Framer Motion).
    -   Responsive Behavior (Mobile-First deep thought).
    -   Accessibility (WCAG 2.1).

### 3.3. CONVERSION CLOSER ("The Salesman")
-   **Filename**: `core/protocols/CONVERSION_CLOSER.md`
-   **Mission**: Maximize R.O.A.S. (Return on Ad Spend).
-   **Cognitive Focus**:
    -   Psychological Triggers (Urgency, Social Proof).
    -   Funnel Architecture (Landing -> Checkout -> Upsell -> Thank You).
    -   Copywriting (Neuro-linguistic programming).

### 3.4. ADS CONNECTOR ("The Integrator")
-   **Filename**: `core/protocols/ADS_CONNECTOR.md`
-   **Mission**: Perfect Tracking & Attribution.
-   **Cognitive Focus**:
    -   **Meta CAPI**: Server-side events with `fbc` and `fbp` parameters.
    -   **Event Match Quality**: Hashing PII (Emails, Phones) before sending.
    -   **Deduplication**: Managing `event_id` synchronization between Pixel and CAPI.

### 3.5. CORE BUILDER ("The Engineer")
-   **Filename**: `core/protocols/CORE_BUILDER.md`
-   **Mission**: Rock-solid Infrastructure.
-   **Cognitive Focus**:
    -   Python/Django/FastAPI best practices.
    -   Database normalization.
    -   Docker/Deployment pipelines.
    -   Security Headers & JWT Authentication.

---

## 4. Execution Roadmap

1.  **Protocol Genesis**: Write the `.md` manifesto for each skill.
2.  **Context Integration**: Ensure the AI loads the specific skill file before acting.
3.  **Pilot Test**: Run a "Simulation" of adding a Meta Lead Event.
    -   Orchestrator plans it.
    -   Builder creates the endpoint.
    -   Connector implements the hashing logic.
    -   Visionary designs the form.
    -   Closer writes the button copy.
