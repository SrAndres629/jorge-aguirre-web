import requests
import json
import os
import sys
import argparse
from colorama import init, Fore, Style

init(autoreset=True)

# CONFIGURATION
API_KEY = "rnd_aZb03HeGwx70HqjHTfcmuNXehGzE"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}
BASE_URL = "https://api.render.com/v1"

class RenderManager:
    def __init__(self):
        self.services = []

    def get_services(self):
        url = f"{BASE_URL}/services"
        r = requests.get(url, headers=HEADERS)
        if r.status_code == 200:
            self.services = r.json()
            return self.services
        return None

    def get_deploy_status(self, service_id):
        url = f"{BASE_URL}/services/{service_id}/deployments"
        r = requests.get(url, headers=HEADERS, params={"limit": 1})
        if r.status_code == 200:
            deploys = r.json()
            return deploys[0]["deployment"]["status"] if deploys else "no_deploys"
        return "error"

    def restart_service(self, service_id):
        print(f"{Fore.YELLOW}🔄 Triggering restart for service {service_id}...")
        url = f"{BASE_URL}/services/{service_id}/deploys"
        r = requests.post(url, headers=HEADERS, json={})
        return r.status_code in [200, 201, 202]

    def get_logs(self, service_id, limit=20):
        # Note: Render API for logs is structured differently or requires a specific stream.
        # For this version, we provide the URL to the logs if we can't fetch them directly via API easily.
        # However, we can fetch recent event logs which are often enough to debug.
        url = f"{BASE_URL}/services/{service_id}/events"
        r = requests.get(url, headers=HEADERS, params={"limit": limit})
        if r.status_code == 200:
            return r.json()
        return []

    def audit(self):
        print(f"{Fore.CYAN}{Style.BRIGHT}--- 🛡️ INFRA GUARDIAN HEALTH AUDIT ---")
        svcs = self.get_services()
        if not svcs:
            print(f"{Fore.RED}❌ Could not connect to Render API.")
            return

        for item in svcs:
            svc = item['service']
            sid = svc['id']
            name = svc['name']
            status = self.get_deploy_status(sid)
            url = svc.get('serviceDetails', {}).get('url', 'N/A')
            
            color = Fore.GREEN if status == "live" else Fore.YELLOW
            if status in ["failed", "canceled"]: color = Fore.RED
            
            print(f"📍 {Fore.WHITE}{name:20} | {Fore.MAGENTA}{sid} | {color}{status.upper():10} | {Fore.BLUE}{url}")

    def update_env(self, service_id, key, value):
        print(f"{Fore.YELLOW}⚙️ Updating Env Var: {key} for {service_id}...")
        url = f"{BASE_URL}/services/{service_id}/env-vars"
        # Render expectes an array of objects
        payload = [{"key": key, "value": value}]
        r = requests.put(url, headers=HEADERS, json=payload)
        return r.status_code == 200

def main():
    parser = argparse.ArgumentParser(description="Render Infrastructure Manager (SRE Tool)")
    parser.add_argument("--audit", action="store_true", help="Run full system audit")
    parser.add_argument("--restart", type=str, help="Restart a specific service ID")
    parser.add_argument("--logs", type=str, help="Get events/logs for a service ID")
    parser.add_argument("--env-set", nargs=3, metavar=('ID', 'KEY', 'VAL'), help="Update env var")
    
    args = parser.parse_args()
    manager = RenderManager()

    if args.audit:
        manager.audit()
    elif args.restart:
        if manager.restart_service(args.restart):
            print(f"{Fore.GREEN}✅ Restart queued.")
        else:
            print(f"{Fore.RED}❌ Restart failed.")
    elif args.logs:
        events = manager.get_logs(args.logs)
        print(f"--- Recent Events for {args.logs} ---")
        for e in events:
            print(f"[{e['timestamp']}] {e['type']}: {e.get('data', {}).get('state', '')}")
    elif args.env_set:
        if manager.update_env(args.env_set[0], args.env_set[1], args.env_set[2]):
             print(f"{Fore.GREEN}✅ Env var updated.")
        else:
             print(f"{Fore.RED}❌ Update failed.")
    else:
        manager.audit()

if __name__ == "__main__":
    main()
