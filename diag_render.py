import requests
import json

API_KEY = "rnd_aZb03HeGwx70HqjHTfcmuNXehGzE"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

def inspect_deploys(sid):
    # Try both /deploys and /deployments
    for ep in ["deploys", "deployments"]:
        url = f"https://api.render.com/v1/services/{sid}/{ep}"
        print(f"Testing {url}...")
        r = requests.get(url, headers=HEADERS)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            try:
                data = r.json()
                print(f"Success! Keys in first element: {data[0].keys() if data else 'Empty'}")
                return ep
            except:
                print("Failed to parse JSON")
    return None

if __name__ == "__main__":
    # Use natalia-brain ID
    inspect_deploys("srv-d5s7pr49c44c73ep2ocg")
