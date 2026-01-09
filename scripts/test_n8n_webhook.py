
import requests
import json
import uuid

# URL of the n8n webhook we just deployed
WEBHOOK_URL = "http://localhost:5678/webhook/website-events"

def test_webhook():
    print(f"📡 Testing n8n Webhook: {WEBHOOK_URL}...")
    
    payload = {
        "event_name": "Lead",
        "user_data": {
            "name": "Integration Test User",
            "phone": "59100000000"
        },
        "utm_data": {
            "utm_campaign": "W-004 Verification"
        }
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        response.raise_for_status()
        print(f"✅ Success! Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_webhook()
