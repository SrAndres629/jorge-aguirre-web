# 🗺️ PROJECT STRUCTURE MAP (Enhanced)

This document visualizes the architecture of **Jorge Aguirre Web** to guide the Distributed Intelligence Triad.

## 🧱 High-Level Architecture

```mermaid
graph TD
    User((User Devices)) -->|HTTPS| RenderLB[Render Load Balancer]
    RenderLB -->|Port 8000| Web([FastAPI / Web Container])
    
    subgraph "Docker Ecosystem (Local/Render)"
        Web -->|Config| Config{Settings Singleton}
        Web -->|Write| DB[(PostgreSQL)]
        Web -->|Enqueue| Redis[(Redis Broker)]
        
        Redis -->|Consume| Worker([Celery Workers])
        
        EvoAPI[Evolution API] -->|WhatsApp| Meta[Meta / WhatsApp]
        EvoAPI -->|Webhook| n8n([n8n Automation])
        
        n8n -->|Command| Antigravity([Antigravity Agent])
    end
    
    Antigravity -->|SSH/Edit| Web
    n8n -->|Trigger| Worker
```

## 📂 Directory Topography

### 🟢 `core/` (The Application Heart)
- **`app/`**: Python logic (Routes, Models, Services).
- **`database/`**: Migrations & SQLite Fallback.
- **`static/`**: Frontend Assets (Images, CSS, JS).
- **`templates/`**: Jinja2 UI.

### 🟡 `automation/` (The Nervous System)
- Contains n8n Workflow JSONs.
- "Natalia" CRM Logic definitions.

### 🔴 `infrastructure/` (The Skeleton)
- `docker/`: Dockerfiles for auxiliary services.
- `antigravity.Dockerfile`: Local AI Agent definition.

---



---
*Synchronized with CAPACIDADES_Y_ORDENES.md*
