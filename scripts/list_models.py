
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    # Fallback just in case env loading fails here too (since I'm running outside core logic)
    api_key = "AIzaSyAY3J9NoQYQr86enTwlOyajzTxlaZcYzn8"

genai.configure(api_key=api_key)

print(f"🔑 API Key Loaded: {api_key[:5]}...")

try:
    print("🔍 Listing models...")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f" - {m.name}")
except Exception as e:
    print(f"❌ Error listing models: {e}")
