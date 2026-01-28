import sqlite3
import os

db_path = os.path.join(os.getcwd(), "natalia-brain", "database", "local_fallback.db")

try:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    print("\n--- CONTACTS (Last 3) ---")
    # Corrected columns: full_name, whatsapp_number
    rows = list(cur.execute("SELECT full_name, whatsapp_number FROM contacts ORDER BY created_at DESC LIMIT 3"))
    if not rows:
        print("(No contacts found)")
    else:
        for row in rows:
            print(f"👤 {row[0]} | 📱 {row[1]}")

    print("\n--- MESSAGES (Last 5) ---")
    # Columns: role, content
    rows = list(cur.execute("SELECT role, content FROM messages ORDER BY created_at DESC LIMIT 5"))
    if not rows:
        print("(No messages found)")
    else:
        for row in rows:
            sender = "🤖 Natalia" if row[0] == "assistant" else "👤 User"
            print(f"{sender}: {row[1]}")

    conn.close()
except Exception as e:
    print(f"❌ Error: {e}")
