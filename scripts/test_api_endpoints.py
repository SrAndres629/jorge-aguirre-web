
import requests
import json
import uuid

BASE_URL = "http://localhost:8000"

def test_lead_endpoint():
    print(f"📡 Testing POST {BASE_URL}/track/lead...")
    payload = {
        "whatsapp_phone": f"591{uuid.uuid4().int}"[:11], # Random valid-ish phone
        "meta_lead_id": "api_test_lead_id",
        "name": "API Verification User",
        "email": "api@test.com"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/track/lead", json=payload)
        response.raise_for_status()
        data = response.json()
        print(f"✅ Success! Response: {data}")
        return data.get("event_id")
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'response' in locals():
            print(f"Response Body: {response.text}")
        return None

def test_interaction_endpoint(lead_id):
    print(f"💬 Testing POST {BASE_URL}/track/interaction...")
    payload = {
        "lead_id": lead_id,
        "role": "user",
        "content": "Hello from API Test Script"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/track/interaction", json=payload)
        response.raise_for_status()
        print(f"✅ Success! Response: {response.json()}")
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'response' in locals():
            print(f"Response Body: {response.text}")

if __name__ == "__main__":
    lead_id = test_lead_endpoint()
    if lead_id:
        test_interaction_endpoint(lead_id)
