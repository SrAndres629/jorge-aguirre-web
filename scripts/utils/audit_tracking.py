import requests
import time

URL = "http://localhost:8000/track/event"
EXTERNAL_ID = "audit_user_2b_001"

payload = {
    "event_name": "PageView",
    "event_time": int(time.time()),
    "event_id": f"audit_pv_{int(time.time())}",
    "user_data": {
        "external_id": EXTERNAL_ID
    },
    "custom_data": {
        "utm_source": "audit_jorge",
        "utm_medium": "integral_2b",
        "utm_campaign": "rescate_tracking_final",
        "fbclid": "audit_fbclid_999"
    },
    "event_source_url": "http://localhost:8000/audit-page",
    "action_source": "website"
}

try:
    print(f"📡 Sending audit event to {URL}...")
    response = requests.post(URL, json=payload, timeout=10)
    print(f"✅ Response ({response.status_code}): {response.json()}")
    
    # Simulate a Lead event too
    lead_payload = payload.copy()
    lead_payload["event_name"] = "Lead"
    lead_payload["event_id"] = f"audit_lead_{int(time.time())}"
    lead_payload["custom_data"]["phone"] = "59164714751"
    
    print(f"📡 Sending Lead audit event...")
    response_lead = requests.post(URL, json=lead_payload, timeout=10)
    print(f"✅ Response ({response_lead.status_code}): {response_lead.json()}")

except Exception as e:
    print(f"❌ Error: {e}")
