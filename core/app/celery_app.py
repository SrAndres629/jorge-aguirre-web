# =================================================================
# CELERY APP CONFIGURATION
# Jorge Aguirre Flores Web
# =================================================================
CELERY_BROKER_URL = settings.CELERY_BROKER_URL
CELERY_RESULT_BACKEND = settings.CELERY_RESULT_BACKEND

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
