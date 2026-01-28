
import sys
import os
import asyncio
import logging

# Setup Path
sys.path.append(os.getcwd())

# Mock Environment
os.environ["DATABASE_URL"] = "postgresql://postgres.eycumxvxyqzznjkwaumx:Omegated669!@aws-0-us-west-2.pooler.supabase.com:6543/postgres"
# Mock Google API Key to test logic flow even if call fails
os.environ["GOOGLE_API_KEY"] = "dummy_key_for_flow_test" 

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SURJECTIVITY_TEST")

async def prove_surjectivity():
    print("📐 TEOREMA DE SURJECTIVIDAD: Comprobando f(m) -> r")
    
    try:
        from app.natalia import natalia
        from app.database import get_chat_history
        
        phone = "59178113055"
        text = "SYSTEM_INTEGRITY_CHECK_DELTA_ZERO"
        
        print(f"1️⃣  INJECTION: f({phone}, '{text}')")
        
        # We call process_message directly to see the crash
        result = await natalia.process_message(phone, text)
        
        print(f"   👉 RAW OUTPUT: {result}")
        
        if result.get("metadata", {}).get("security_block"):
             print("   🛡️ BLOCKED by Security Sentinel (Expected if prompt unsafe)")
        
        reply = result.get("reply", "")
        print(f"   🤖 REPLY: {reply}")
        
        if "refresh" in reply.lower() or "disculpa" in reply.lower():
            print("   ❌ FAILURE: Cognitive Failure Detected (The Catch Block caught it).")
            # We need to see the real error. 
            # Since natalia.py catches it, we can't see it here unless we modify natalia.py or rely on the logs printed by our new Shield.
            print("   ⚠️ Check the logs above for 'SHIELD ACTIVATED'.")
            
        else:
             print("   ✅ SUCCESS: Logic Loop Completed.")

    except ImportError as e:
        print(f"❌ CRITICAL IMPORT ERROR: {e}")
    except Exception as e:
        print(f"❌ UNHANDLED EXCEPTION: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(prove_surjectivity())
