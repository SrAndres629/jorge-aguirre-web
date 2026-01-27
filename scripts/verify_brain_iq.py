
import sys
import os
import time

# Add core to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))

from app.natalia import natalia

def test_cognition(test_name, phone, input_text, expected_keyword=None, meta_data=None):
    print(f"\n🔬 TEST: {test_name}")
    print(f"   Input: '{input_text}'")
    
    start = time.time()
    try:
        result = natalia.process_message(phone, input_text, meta_data)
        elapsed = round(time.time() - start, 2)
        
        reply = result.get("reply", "")
        print(f"   🤖 Output ({elapsed}s): {reply}")
        
        if expected_keyword:
            if expected_keyword.lower() in reply.lower():
                print("   ✅ PASSED (Keyword found)")
            else:
                print(f"   ⚠️ WARNING (Keyword '{expected_keyword}' not found)")
        else:
            print("   ✅ PASSED (Response generated)")
            
    except Exception as e:
        print(f"   ❌ FAILED: {e}")

if __name__ == "__main__":
    print("🦅 COGNITIVE SINGULARITY VERIFICATION PROTOCOL")
    print("=============================================")
    
    # 1. System Prompt & Pricing Logic
    test_cognition(
        "Pricing Inquiry (Virgin Skin)", 
        "59177777777", 
        "Hola, quiero saber precio de microblading. Nunca me hice nada.",
        expected_keyword="1500" # Should mention 1500 Bs or $215
    )
    
    # 2. Context/Memory Check (Simulated by sequence)
    # Note: DB saves history, so running this twice will create memory.
    test_cognition(
        "Memory Injection 1", 
        "59188888888", 
        "Me llamo Sofia y vivo en Warnes.",
        expected_keyword="Sofia"
    )
    
    test_cognition(
        "Memory Retrieval 2", 
        "59188888888", 
        "¿Recuerdas cómo me llamo?",
        expected_keyword="Sofia"
    )
    
    # 3. Strategy Check (Location)
    test_cognition(
        "Sales Strategy (Location)", 
        "59177777777", 
        "Donde es el lugar?",
        expected_keyword="Equipetrol"
    )
