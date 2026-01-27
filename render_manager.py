import requests
import json
import os
import sys

API_KEY = "rnd_aZb03HeGwx70HqjHTfcmuNXehGzE"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

def get_services():
    url = "https://api.render.com/v1/services"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching services: {response.status_code} - {response.text}")
        return None

def get_deployment_status(service_id):
    url = f"https://api.render.com/v1/services/{service_id}/deployments"
    response = requests.get(url, headers=HEADERS, params={"limit": 1})
    if response.status_code == 200:
        deploys = response.json()
        if deploys:
            return deploys[0]["deployment"]["status"]
    return "unknown"

def monitor():
    print("--- RENDER INFRASTRUCTURE STATUS ---")
    services = get_services()
    if not services:
        return

    for item in services:
        svc = item['service']
        sid = svc['id']
        name = svc['name']
        status = get_deployment_status(sid)
        ext_url = svc.get('serviceDetails', {}).get('url', 'N/A')
        print(f"Service: {name:25} | ID: {sid} | Status: {status:10} | URL: {ext_url}")

if __name__ == "__main__":
    monitor()
