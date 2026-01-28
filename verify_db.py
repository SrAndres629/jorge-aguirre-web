import sqlite3
import os

# Path relative to CWD (jorge_web)
db_path = os.path.join(os.getcwd(), "natalia-brain", "database", "local_fallback.db")

print(f"Target DB: {db_path}")

if not os.path.exists(db_path):
    print("❌ No DB file found at target path.")
    exit()

try:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    print("\n--- CONTACTS ---")
    rows = list(cur.execute("SELECT name, phone FROM contacts ORDER BY created_at DESC LIMIT 3"))
    if not rows:
        print("(No contacts)")
    for row in rows:
        print(f"{row[0]} - {row[1]}")
        
    print("\n--- MESSAGES ---")
    rows = list(cur.execute("SELECT role, content FROM messages ORDER BY timestamp DESC LIMIT 3"))
    if not rows:
        print("(No messages)")
    for row in rows:
        print(f"{row[0]}: {row[1]}")

    conn.close()
except Exception as e:
    print(f"❌ Error: {e}")
