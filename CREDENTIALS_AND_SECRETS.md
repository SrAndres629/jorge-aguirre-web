# 🔐 Jorge Aguirre Web - Project Credentials & Secrets

> [!IMPORTANT]
> **Confidential Document** - Do not share this file publicly.
> This file contains local development credentials and internal networking configurations.

## 🐘 Database (PostgreSQL)

Used by Evolution API and n8n for persistence.

| Parameter | Value | Context |
| :--- | :--- | :--- |
| **Host (Internal)** | `postgres_evolution` | Use this inside n8n or other Docker containers. |
| **Host (External)** | `localhost` (If mapped) | Currently NOT mapped to host port. |
| **Port** | `5432` | Standard PostgreSQL port. |
| **Database Name** | `evolution` | Main database. |
| **User** | `evolution` | Admin user. |
| **Password** | `evolution_password` | Admin password. |

---

## 🤖 Evolution API

WhatsApp Gateway Service.

| Parameter | Value | Use Case |
| :--- | :--- | :--- |
| **Manager URL** | `http://localhost:8081` | Access via Browser. |
| **API Key** | `B89599B2-37E4-4DCA-92D3-87F8674C7D69` | Authentication Header (`apikey`). |
| **Instance Name** | `JorgeMain` | Main WhatsApp instance name. |
| **Internal URL** | `http://evolution_api:8080` | Use this inside n8n to call API. |

---

## 🧠 n8n Automation

Workflow automation engine.

| Parameter | Value | Use Case |
| :--- | :--- | :--- |
| **Editor URL** | `http://localhost:5678` | Access via Browser. |
| **Webhook URL** | `http://host.docker.internal:5678` | Use this in Evolution API to send data to n8n. |

---

## ⚡ Redis

Caching layer for Evolution API.

| Parameter | Value | Context |
| :--- | :--- | :--- |
| **Host** | `redis_evolution` | Internal Docker usage. |
| **Port** | `6379` | Standard Redis port. |

## 🔑 Environment Variables (.env)

Critical variables loaded by `docker-compose.yml` and `app/config.py`.

```bash
# Evolution API
AUTHENTICATION_API_KEY=B89599B2-37E4-4DCA-92D3-87F8674C7D69
SERVER_URL=http://localhost:8081
CONFIG_SESSION_PHONE_VERSION=2.3000.1015901307

# Database
DATABASE_URL=postgresql://evolution:evolution_password@postgres_evolution:5432/evolution

# Networking
WEBHOOK_URL=http://localhost:5678/
```

## ⚡ Supabase (Cloud Database)

External PostgreSQL database for CRM and persistent data.

| Parameter | Value | Context |
| :--- | :--- | :--- |
| **Host** | `aws-0-us-west-2.pooler.supabase.com` | Cloud Host (Pooler). |
| **Database** | `postgres` | Default DB name. |
| **User** | `postgres.eycumxvxyqzznjkwaumx` | Connection User. |
| **Password** | `Omegated669!` | **Sensitive**. |
| **Port** | `6543` | Connection pool port (Transaction mode). |
| **SSL** | `Allow` / `Require` | **Must enable "Ignore SSL Issues"**. |

