
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load env explicitly
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    print("❌ NO API KEY")
    exit(1)

genai.configure(api_key=API_KEY)

# List of models seen in the user's account + standard ones
candidates = [
    "models/gemini-2.0-flash-lite-preview-02-05",
    "models/gemini-2.0-flash",
    "models/gemini-1.5-flash",
    "models/gemini-pro",
    "models/gemini-pro-latest",
    "models/gemini-flash-latest",
    "models/gemini-2.5-flash-lite", # dashboard name
    "models/gemini-2.0-flash-lite", # potential alias
    "models/gemini-1.0-pro"
]

print(f"🔑 Testing Key: {API_KEY[:10]}... with {len(candidates)} candidates")

suggestion = None

for model_name in candidates:
    print(f"👉 Testing: {model_name}...", end=" ")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Say 'OK'")
        print(f"✅ SUCCESS! Output: {response.text.strip()}")
        suggestion = model_name
        break
    except Exception as e:
        print(f"❌ FAILED. Reason: {str(e)[:100]}...")

if suggestion:
    print(f"\n🎉 WINNER: {suggestion}")
    print("Update natalia.py with this model name.")
else:
    print("\n💀 ALL MODELS FAILED. Check API Key permissions or Billing.")
