# =================================================================
# CELERY APP CONFIGURATION
# Jorge Aguirre Flores Web
# =================================================================
from celery import Celery
from app.config import settings

CELERY_BROKER_URL = settings.CELERY_BROKER_URL
CELERY_RESULT_BACKEND = settings.CELERY_RESULT_BACKEND

celery_app = Celery(
    "jorge_worker",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["app.tasks"]
)

# Detect if we are in a "No Redis" environment
# If the URL is the default internal docker alias but we are not in that specific docker network,
# OR if explicitly requested via env var.
FORCE_EAGER = False

# Simple heuristic: If we are on a platform that might not have Redis linked (like a simple Render Web Service without a Redis instance attached)
# We default to Eager mode to prevent crashes.
import os
if os.getenv("CELERY_TASK_ALWAYS_EAGER", "False").lower() in ("true", "1", "yes"):
    FORCE_EAGER = True

# Also check for default "redis_evolution" hostname which implies Docker Compose
if "redis_evolution" in CELERY_BROKER_URL:
    # We warn but don't force unless we can't resolve it (could add DNS check, but let's stick to env var for now)
    # Actually, for Render Web Service standalone, this Hostname won't resolve.
    pass

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/La_Paz",
    enable_utc=True,
    broker_connection_retry_on_startup=True,
    task_acks_late=True,
    task_always_eager=FORCE_EAGER  # <--- CRITICAL FIX
)

if FORCE_EAGER:
    print("⚠️  WARNING: Celery running in ALWAYS_EAGER mode (No Redis). Background tasks will block.")

if __name__ == "__main__":
    celery_app.start()
