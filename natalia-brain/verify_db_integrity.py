
import sys
import os
import asyncio
import logging

# Setup Path to see 'app'
sys.path.append(os.getcwd())

# Mock Environment
os.environ["DATABASE_URL"] = "postgresql://postgres.eycumxvxyqzznjkwaumx:Omegated669!@aws-0-us-west-2.pooler.supabase.com:6543/postgres"

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DB_DEBUG")

async def test_critical_path():
    print("🧪 STARTING MATHEMATICAL FLOW TEST...")
    
    try:
        from app.database import get_or_create_lead, log_interaction
        from app.sql_queries import SELECT_LEAD_ID_BY_PHONE
        
        phone = "59178113055"
        text = "TEST_MESSAGE_MATHEMATICAL_ANALYSIS"
        
        print(f"1️⃣  TESTING: get_or_create_lead('{phone}')")
        lead_id, is_new = get_or_create_lead(phone, {})
        
        print(f"   ✅ RESULT: Lead ID={lead_id} | Is New={is_new}")
        
        print(f"2️⃣  TESTING: log_interaction('{lead_id}', 'user', '{text}')")
        success = log_interaction(lead_id, "user", text)
        
        if success:
            print("   ✅ RESULT: Interaction Logged Successfully")
        else:
            print("   ❌ RESULT: Failed to log interaction (returned False)")

    except ImportError as e:
        print(f"❌ CRITICAL IMPORT ERROR: {e}")
        print("   -> This means the file structure move (core -> natalia-brain) broke imports.")
    except Exception as e:
        print(f"❌ CRITICAL RUNTIME ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_critical_path())
