import requests
import json

API_KEY = "rnd_aZb03HeGwx70HqjHTfcmuNXehGzE"
SERVICE_ID = "srv-d5s7pr49c44c73ep2ocg"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json"
}

def check_env_vars():
    print("--- ENV VARS ---")
    url = f"https://api.render.com/v1/services/{SERVICE_ID}/env-vars"
    r = requests.get(url, headers=HEADERS)
    if r.status_code == 200:
        for item in r.json():
            ev = item['envVar']
            val = ev['value']
            # Mask sensitive info
            masked = val[:5] + "..." if val else "None"
            print(f"{ev['key']}: {masked}")
    else:
        print(f"Error: {r.status_code} - {r.text}")

def check_latest_deploy():
    print("\n--- LATEST DEPLOY ---")
    url = f"https://api.render.com/v1/services/{SERVICE_ID}/deployments"
    r = requests.get(url, headers=HEADERS, params={"limit": 1})
    if r.status_code == 200:
        deploys = r.json()
        if deploys:
            d = deploys[0]['deployment']
            print(f"ID: {d['id']}")
            print(f"Status: {d['status']}")
            print(f"Created: {d['createdAt']}")
    else:
        print(f"Error: {r.status_code} - {r.text}")

if __name__ == "__main__":
    check_env_vars()
    check_latest_deploy()
