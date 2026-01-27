
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load explicitly from root
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    print("❌ NO API KEY FOUND IN ENV")
    exit(1)

print(f"🔑 Testing Key: {API_KEY[:10]}...")

genai.configure(api_key=API_KEY)

print("-" * 20)
print("Testing gemini-1.5-flash...")
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Di 'Hola Flash'")
    print(f"✅ Success: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

print("-" * 20)
print("Testing models/gemini-1.5-flash...")
try:
    model = genai.GenerativeModel('models/gemini-1.5-flash')
    response = model.generate_content("Di 'Hola Flash Models'")
    print(f"✅ Success: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

print("-" * 20)
print("Testing gemini-pro...")
try:
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Di 'Hola Pro'")
    print(f"✅ Success: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")
