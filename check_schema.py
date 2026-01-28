import sqlite3
import os

db_path = os.path.join(os.getcwd(), "natalia-brain", "database", "local_fallback.db")

print(f"DB: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    print("--- CONTACTS COLUMNS ---")
    cur.execute("PRAGMA table_info(contacts)")
    for col in cur.fetchall():
        print(col)

    print("\n--- MESSAGES COLUMNS ---")
    cur.execute("PRAGMA table_info(messages)")
    for col in cur.fetchall():
        print(col)
        
    conn.close()
except Exception as e:
    print(e)
