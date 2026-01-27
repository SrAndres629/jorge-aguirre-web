
import requests
import os
import json
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
API_KEY = os.getenv("GOOGLE_API_KEY")

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

headers = {
    'Content-Type': 'application/json'
}

data = {
    "contents": [{
        "parts": [{"text": "Explain how AI works in one sentence."}]
    }]
}

print(f"📡 Testing REST API: {url.split('key=')[0]}...[KEY]")

try:
    response = requests.post(url, headers=headers, json=data)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("✅ SUCCESS!")
        print(response.json()['candidates'][0]['content']['parts'][0]['text'])
    else:
        print("❌ FAILED!")
        print(response.text)
except Exception as e:
    print(f"❌ EXCEPTION: {e}")
