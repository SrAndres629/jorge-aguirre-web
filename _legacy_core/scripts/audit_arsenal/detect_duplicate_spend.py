
import sys
import os
from datetime import datetime, timedelta

# Add core to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.database import get_cursor

def detect_duplicates():
    print("🕵️  DATA FORENSIC AUDIT: Duplicate Spend Hunter")
    print("="*60)
    
    with get_cursor() as cur:
        # 1. Search for repeated conversion marks in contacts for same IP (if multiple contacts share IP)
        cur.execute("""
            SELECT ip_address, COUNT(*) as lead_count
            FROM visitors
            WHERE source = 'conversion' OR source = 'whatsapp_click'
            GROUP BY ip_address
            HAVING COUNT(*) > 1
            ORDER BY lead_count DESC
            LIMIT 20
        """)
        repeat_ips = cur.fetchall()
        
        # 2. Search for multiple conversion attempts in 24h
        day_ago = datetime.now() - timedelta(hours=24)
        cur.execute("""
            SELECT external_id, COUNT(*) as attempts
            FROM visitors
            WHERE timestamp > %s
            GROUP BY external_id
            HAVING COUNT(*) > 1
        """, (day_ago,))
        frequent_visitors = cur.fetchall()

    print(f"🚩 Potential Multi-Conversion IPs (Ad Spend Risk): {len(repeat_ips)}")
    for ip, count in repeat_ips:
        print(f"   ∟ IP: {ip} triggered {count} events.")

    print(f"🚩 Aggressive Re-visitors (Last 24h): {len(frequent_visitors)}")
    
    if len(repeat_ips) > 0:
        waste_estimate = len(repeat_ips) * 5 # Assuming 5 Bs per lead waste
        print(f"\n💸 ESTIMATED AD SPEND WASTE: ~{waste_estimate} Bs.")
        print("⚠️  RECOMENDACIÓN: Reforzar el 'Deduplication Shield' en el Client-Side.")
    else:
        print("\n✅ NO DUPLICATE SPEND DETECTED.")
        print("   Tu 'Conversion Shield' está protegiendo el presupuesto eficientemente.")
    print("="*60 + "\n")

if __name__ == "__main__":
    try:
        detect_duplicates()
    except Exception as e:
        print(f"❌ Error during Duplicate Audit: {e}")
