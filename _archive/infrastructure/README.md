# 🧠 INFRASTRUCTURE MEMORY: Docker & AI

**Dominio**: `Antigravity` (EXCLUSIVO - Zona Roja)

## 🐳 Contenedores Críticos
| Servicio | Puerto | Rol |
| :--- | :--- | :--- |
| `web` | 8000 | App Principal |
| `evolution_api` | 8081 | WhatsApp Gateway |
| `antigravity` | 2222 | Local AI (SSH) |

## 🤖 Antigravity Agent
- **Modelo**: `qwen2.5-coder:7b`
- **Volumen**: `antigravity_data` (Persistente)

## 📡 Acceso SSH (Puerto 2222)
Habilitado para **Antigravity** (IDE) y **n8n**.
- **Comando Manual**: `ssh agent@localhost -p 2222`
- **Password**: `antigravity`

## 🛡️ Seguridad
- No editar `Dockerfile` sin pasar por el proceso de `gemini audit`.
