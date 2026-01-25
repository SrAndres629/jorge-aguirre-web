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
    broker_url = celery_app.conf.broker_url
    
    print(f"[-] task_always_eager: {is_eager}")
    print(f"[-] broker_url: {broker_url}")
    
    if is_eager and "memory://" in broker_url:
        print("✅ SUCCESS: Celery is in EAGER mode AND using Memory Broker (Safe for No-Redis env)")
        sys.exit(0)
    else:
        print(f"❌ FAILURE: Mismatch. Eager={is_eager}, Broker={broker_url}")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ CRITICAL ERROR: {e}")
    sys.exit(1)
