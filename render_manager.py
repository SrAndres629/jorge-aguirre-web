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
        url = f"{BASE_URL}/services/{service_id}/deploys"
        try:
            r = requests.get(url, headers=HEADERS, params={"limit": 1}, timeout=10)
            if r.status_code == 200:
                deploys = r.json()
                if deploys and isinstance(deploys, list):
                    # Confirmed: First element has 'deploy' key
                    first = deploys[0]
                    if 'deploy' in first:
                        return first["deploy"]["status"]
                    return "unknown_structure"
                return "no_deploys"
            return f"err_{r.status_code}"
        except Exception as e:
            return f"conn_err: {str(e)[:20]}"

    def restart_service(self, service_id):
        print(f"{Fore.YELLOW}🔄 Triggering restart for service {service_id}...")
        url = f"{BASE_URL}/services/{service_id}/deploys"
        r = requests.post(url, headers=HEADERS, json={})
        return r.status_code in [200, 201, 202]

    def get_logs(self, service_id, limit=20):
        """Fetch recent service events (Log equivalents for control plane)"""
        url = f"{BASE_URL}/services/{service_id}/events"
        r = requests.get(url, headers=HEADERS, params={"limit": limit})
        if r.status_code == 200:
            return r.json()
        return []

    def deep_scan(self, service_id):
        """Performs a deep diagnostic scan of a single service"""
        print(f"{Fore.YELLOW}🔍 Deep Diagnostic Scan for: {service_id}")
        
        # 1. Check Env Vars
        print(f"   --- Environment Variables ---")
        ev_url = f"{BASE_URL}/services/{service_id}/env-vars"
        ev_r = requests.get(ev_url, headers=HEADERS)
        if ev_r.status_code == 200:
            vars_list = ev_r.json()
            critical_vars = ["GOOGLE_API_KEY", "EVOLUTION_API_URL", "DATABASE_URL"]
            found = [v['envVar']['key'] for v in vars_list]
            for cv in critical_vars:
                status = f"{Fore.GREEN}✅ Found" if cv in found else f"{Fore.RED}❌ MISSING"
                print(f"   {status} {cv}")
        
        # 2. Check Latest Events for Failures
        print(f"\n   --- Recent Critical Events ---")
        events = self.get_logs(service_id, limit=5)
        for e in events:
            evt = e.get('event', e)
            ts = evt.get('timestamp', 'N/A')
            etype = evt.get('type', 'unknown')
            color = Fore.RED if "error" in etype.lower() or "fail" in etype.lower() else Fore.WHITE
            print(f"   {color}[{ts}] {etype}")

    def audit(self):
        """High-level system audit"""
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
            
            print(f"📍 {Fore.WHITE}{name:20} | {Fore.MAGENTA}{sid} | {color}{status.upper():10}")
            print(f"   🔗 {Fore.BLUE}{url}\n")

    def update_env(self, service_id, key, value):
        print(f"{Fore.YELLOW}⚙️ Updating Env Var: {key} for {service_id}...")
        url = f"{BASE_URL}/services/{service_id}/env-vars"
        payload = [{"key": key, "value": value}]
        r = requests.put(url, headers=HEADERS, json=payload)
        return r.status_code == 200

def main():
    parser = argparse.ArgumentParser(description="Render SRE Controller (Infra Guardian)")
    parser.add_argument("--audit", action="store_true", help="Run full system audit")
    parser.add_argument("--scan", type=str, help="Deep diagnostic scan of a service ID")
    parser.add_argument("--restart", type=str, help="Restart a specific service ID")
    parser.add_argument("--logs", type=str, help="Get recent events for a service ID")
    parser.add_argument("--env-set", nargs=3, metavar=('ID', 'KEY', 'VAL'), help="Update env var")
    
    args = parser.parse_args()
    manager = RenderManager()

    if args.audit:
        manager.audit()
    elif args.scan:
        manager.deep_scan(args.scan)
    elif args.restart:
        if manager.restart_service(args.restart):
            print(f"{Fore.GREEN}✅ Restart queued.")
        else:
            print(f"{Fore.RED}❌ Restart failed.")
    elif args.logs:
        events = manager.get_logs(args.logs)
        print(f"--- Recent Events for {args.logs} ---")
        for e in events:
            evt = e.get('event', e)
            print(f"[{evt.get('timestamp')}] {evt.get('type')}")
    elif args.env_set:
        if manager.update_env(args.env_set[0], args.env_set[1], args.env_set[2]):
             print(f"{Fore.GREEN}✅ Env var updated.")
        else:
             print(f"{Fore.RED}❌ Update failed.")
    else:
        manager.audit()

if __name__ == "__main__":
    main()
