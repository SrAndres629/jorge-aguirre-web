import requests
import json

API_KEY = "rnd_aZb03HeGwx70HqjHTfcmuNXehGzE"
SERVICE_ID = "srv-d5s7pr49c44c73ep2ocg"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# Values from .env and previous session
ENV_VARS = [
    {"key": "EVOLUTION_API_URL", "value": "https://evolution-whatsapp-zn13.onrender.com"},
    {"key": "EVOLUTION_API_KEY", "value": "JorgeSecureKey123"},
    {"key": "EVOLUTION_INSTANCE", "value": "NataliaCoreV1"},
    {"key": "DATABASE_URL", "value": "postgresql://postgres.eycumxvxyqzznjkwaumx:Omegated669!@aws-0-us-west-2.pooler.supabase.com:6543/postgres?pgbouncer=true&connection_limit=1"},
    {"key": "GOOGLE_API_KEY", "value": "AIzaSyAT8D5oWUqVn5Ex0-UpcYmtlSZj6S1nzcw"},
    {"key": "ADMIN_KEY", "value": "Andromeda2025"},
    {"key": "PYTHON_VERSION", "value": "3.11.0"}
]

def restore():
    print("--- RESTORING PRODUCTION ENV ---")
    url = f"https://api.render.com/v1/services/{SERVICE_ID}/env-vars"
    r = requests.put(url, headers=HEADERS, json=ENV_VARS)
    if r.status_code in [200, 201]:
        print("✅ Environment variables restored successfully.")
        # Trigger redeploy
        deploy_url = f"https://api.render.com/v1/services/{SERVICE_ID}/deploys"
        rd = requests.post(deploy_url, headers=HEADERS, json={})
        if rd.status_code == 202:
            print("🚀 Redeploy triggered.")
    else:
        print(f"❌ Error: {r.status_code} - {r.text}")

if __name__ == "__main__":
    restore()
