import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def verify_gemini():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ Error: GOOGLE_API_KEY not found in .env")
        return

    print(f"🔍 Testing Gemini API with key starting in: {api_key[:5]}...")
    
    # Simple model list or generation test
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    
    try:
        r = requests.get(url)
        if r.status_code == 200:
            models = r.json()
            print("✅ Connection Successful. Models available:")
            # Check for gemini-1.5-flash or pro
            available = [m['name'] for m in models.get('models', []) if 'gemini' in m['name'].lower()]
            for m in available[:3]:
                print(f"   - {m}")
            return True
        else:
            print(f"❌ API Error: {r.status_code} - {r.text}")
            return False
    except Exception as e:
        print(f"❌ Connection Exception: {e}")
        return False

if __name__ == "__main__":
    verify_gemini()
