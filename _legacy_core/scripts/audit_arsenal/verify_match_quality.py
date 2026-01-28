
import sys
import os
import logging

# Add core to path to import app.database
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.database import get_cursor, BACKEND

def run_quality_audit():
    print(f"🕵️  DATA FORENSIC AUDIT: Match Quality Check ({BACKEND})")
    print("="*60)
    
    with get_cursor() as cur:
        # 1. Total Leads in contacts
        cur.execute("SELECT COUNT(*) FROM contacts")
        total_leads = cur.fetchone()[0]
        
        if total_leads == 0:
            print("❌ No leads found in 'contacts' table.")
            return

        # 2. Rich Data Counts
        cur.execute("SELECT COUNT(*) FROM contacts WHERE fb_click_id IS NOT NULL")
        has_fbc = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM contacts WHERE fb_browser_id IS NOT NULL")
        has_fbp = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM contacts WHERE whatsapp_number IS NOT NULL")
        has_phone = cur.fetchone()[0]

        # In Natalia schema, we might not store actual email, but let's check leads table too
        cur.execute("SELECT COUNT(*) FROM leads WHERE email IS NOT NULL")
        has_email = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM leads")
        total_rescue_leads = cur.fetchone()[0]

    # Metrics Calculation
    fbc_rate = (has_fbc / total_leads) * 100
    fbp_rate = (has_fbp / total_leads) * 100
    phone_rate = (has_phone / total_leads) * 100
    
    # EMQ Score (Custom Calculation for Meta Attribution)
    # Weights: Phone (1.0), FBC (0.8), FBP (0.6), Email (1.0)
    # Normalized to 10
    score = ( (fbc_rate * 0.8) + (fbp_rate * 0.6) + (phone_rate * 1.0) ) / 24 # Simplified normalized score
    emq = min(score, 10)

    print(f"📊 Total Entities (CRM): {total_leads}")
    print(f"📊 Total Rescue Leads:   {total_rescue_leads}")
    print("-" * 60)
    print(f"✅ Has FB Click ID (fbc):  {has_fbc} ({fbc_rate:.1f}%)")
    print(f"✅ Has FB Browser ID (fbp): {has_fbp} ({fbp_rate:.1f}%)")
    print(f"✅ Has Phone (ph):         {has_phone} ({phone_rate:.1f}%)")
    print(f"✅ Has Email (em):         {has_email} ({ (has_email/max(total_rescue_leads, 1))*100:.1f}%)")
    print("-" * 60)
    print(f"🏆 ESTIMATED EVENT MATCH QUALITY (EMQ): {emq:.1f}/10.0")
    
    if emq < 6:
        print("\n⚠️  ALERT: LOW ATTRIBUTION QUALITY")
        print("   Razón: Se están perdiendo señales críticas. Meta no puede atribuir de forma eficiente.")
        print("   Acción: Asegurar que el middleware capture '_fbc' y '_fbp' en el primer toque.")
    else:
        print("\n💎 STATUS: OPTIMUM SIGNAL QUALITY")
        print("   Tu sistema está capturando señales de alta densidad para optimización de ROAS.")
    print("="*60 + "\n")

if __name__ == "__main__":
    try:
        run_quality_audit()
    except Exception as e:
        print(f"❌ Error during Forensic Audit: {e}")
