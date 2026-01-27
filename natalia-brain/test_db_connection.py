import psycopg2
import os
import sys
from dotenv import load_dotenv

# Load env from root
load_dotenv(os.path.join(os.getcwd(), '.env'))

def test_connection():
    db_url = os.getenv("DATABASE_URL")
    print(f"🔌 Testing Connection to: {db_url}")
    
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # Simple query
        cur.execute("SELECT version();")
        version = cur.fetchone()
        
        print(f"✅ SUCCESS: Connected!")
        print(f"📦 Version: {version[0]}")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ CONNECTION FAILED: {e}")

if __name__ == "__main__":
    test_connection()
