# =================================================================
# CELERY APP CONFIGURATION
# Jorge Aguirre Flores Web
# =================================================================
import os
from celery import Celery
from app.config import settings

# Redis URL from environment or default to local docker service
# Note: We use the REDIS configuration from settings ideally, but for now we construct it.
# In config.py we have CACHE_REDIS_URI but typically that's for Evolution.
# Let's assume a standard Redis service 'redis_evolution' on port 6379 DB 1 (DB 0 is for Evolution cache usually)

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis_evolution:6379/1")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis_evolution:6379/1")

celery_app = Celery(
    "jorge_worker",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["app.tasks"]  # We will define tasks in app.tasks.py
)

# Optional: Celery Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/La_Paz",
    enable_utc=True,
    # Resilience settings
    broker_connection_retry_on_startup=True,
    task_acks_late=True, # Ensure task is acked ONLY after completion (prevents data loss on crash)
)

if __name__ == "__main__":
    celery_app.start()
