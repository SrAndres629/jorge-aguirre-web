# scripts/verify_celery_fallback.py
import os
import sys

# Mock environment to simulate missing Redis / Render env
os.environ["CELERY_TASK_ALWAYS_EAGER"] = "True"

try:
    # Add core to path so we can import app
    sys.path.append(os.path.join(os.getcwd(), 'core'))
    from app.celery_app import celery_app
    
    print(f"[-] Checking Celery Configuration...")
    is_eager = celery_app.conf.task_always_eager
    print(f"[-] task_always_eager: {is_eager}")
    
    if is_eager:
        print("✅ SUCCESS: Celery is in EAGER mode (Safe for No-Redis env)")
        sys.exit(0)
    else:
        print("❌ FAILURE: Celery is still trying to use Redis")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ CRITICAL ERROR: {e}")
    sys.exit(1)
