#!/usr/bin/env python3
"""
=================================================================
NEURAL LINK VERIFICATION PROTOCOL - Pre-Flight Check
Jorge Aguirre Flores Web Infrastructure Audit
=================================================================
Certifies that the infrastructure is ready for real-time WhatsApp traffic.
"""
import asyncio
import sys
import os
import time
import socket
from datetime import datetime
from typing import Dict, Any, Optional

# Add core to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))

import httpx

# =================================================================
# CONFIGURATION (Loaded from environment)
# =================================================================
from dotenv import load_dotenv
load_dotenv()

EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL", "http://localhost:8080")
EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY", "")
EVOLUTION_INSTANCE = os.getenv("EVOLUTION_INSTANCE", "JorgeMain")
DATABASE_URL = os.getenv("DATABASE_URL", "")
LOCAL_SERVER_URL = "http://localhost:8000"

# =================================================================
# AUDITORS
# =================================================================

class NeuralLinkAuditor:
    """Pre-flight verification for WhatsApp real-time infrastructure."""
    
    def __init__(self):
        self.results: Dict[str, Dict[str, Any]] = {}
        self.start_time = time.time()
    
    async def check_evolution_connectivity(self) -> Dict[str, Any]:
        """Test 1: Evolution API Basic Ping"""
        test_name = "Evolution API Connectivity"
        try:
            url = f"{EVOLUTION_API_URL.rstrip('/')}/instance/fetch"
            headers = {"apikey": EVOLUTION_API_KEY}
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                start = time.time()
                resp = await client.get(url, headers=headers)
                latency_ms = round((time.time() - start) * 1000, 2)
                
                if resp.status_code == 200:
                    return {"status": "✅ ONLINE", "latency_ms": latency_ms, "passed": True}
                else:
                    return {"status": f"⚠️ HTTP {resp.status_code}", "latency_ms": latency_ms, "passed": False}
        except httpx.ConnectError:
            return {"status": "❌ CONNECTION REFUSED", "latency_ms": None, "passed": False, "hint": "Evolution API not running or unreachable"}
        except Exception as e:
            return {"status": f"❌ ERROR: {e}", "latency_ms": None, "passed": False}
    
    async def check_evolution_instance(self) -> Dict[str, Any]:
        """Test 2: WhatsApp Instance Status"""
        test_name = "Evolution Instance State"
        try:
            url = f"{EVOLUTION_API_URL.rstrip('/')}/instance/connectionState/{EVOLUTION_INSTANCE}"
            headers = {"apikey": EVOLUTION_API_KEY}
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, headers=headers)
                data = resp.json()
                
                # Handle different response formats
                state = data.get('instance', {}).get('state') or data.get('state', 'unknown')
                
                if state == 'open':
                    return {"status": "✅ CONNECTED (open)", "instance": EVOLUTION_INSTANCE, "passed": True}
                elif state == 'close':
                    return {"status": "⚠️ DISCONNECTED (close)", "instance": EVOLUTION_INSTANCE, "passed": False, "hint": "Need to reconnect via QR"}
                else:
                    return {"status": f"⚠️ {state}", "instance": EVOLUTION_INSTANCE, "passed": False}
        except Exception as e:
            return {"status": f"❌ ERROR: {e}", "passed": False}
    
    async def check_webhook_config(self) -> Dict[str, Any]:
        """Test 3: Webhook Configuration"""
        try:
            url = f"{EVOLUTION_API_URL.rstrip('/')}/webhook/find/{EVOLUTION_INSTANCE}"
            headers = {"apikey": EVOLUTION_API_KEY}
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, headers=headers)
                config = resp.json()
                
                webhook_url = config.get('url', 'NOT SET')
                enabled = config.get('enabled', False)
                by_events = config.get('webhookByEvents', False)
                
                issues = []
                if not enabled:
                    issues.append("DISABLED")
                if by_events:
                    issues.append("Event splitting ON (should be OFF)")
                if 'n8n' not in webhook_url.lower() and 'localhost' not in webhook_url.lower():
                    issues.append(f"URL suspicious: {webhook_url}")
                
                if not issues:
                    return {"status": "✅ CONFIGURED", "url": webhook_url, "enabled": enabled, "passed": True}
                else:
                    return {"status": f"⚠️ ISSUES: {', '.join(issues)}", "url": webhook_url, "passed": False}
                    
        except Exception as e:
            return {"status": f"❌ ERROR: {e}", "passed": False}
    
    async def check_database(self) -> Dict[str, Any]:
        """Test 4: PostgreSQL Connectivity"""
        try:
            # Import database module
            from app.database import check_connection, BACKEND
            
            if check_connection():
                return {"status": f"✅ CONNECTED ({BACKEND})", "backend": BACKEND, "passed": True}
            else:
                return {"status": "❌ DISCONNECTED", "passed": False}
        except ImportError as e:
            return {"status": f"⚠️ IMPORT ERROR: {e}", "passed": False, "hint": "Run from project root with correct PYTHONPATH"}
        except Exception as e:
            return {"status": f"❌ ERROR: {e}", "passed": False}
    
    async def check_database_schema(self) -> Dict[str, Any]:
        """Test 5: Verify Critical Tables Exist"""
        try:
            from app.database import get_cursor, BACKEND
            
            required_tables = ['contacts', 'messages', 'leads', 'interactions']
            found_tables = []
            
            with get_cursor() as cur:
                if not cur:
                    return {"status": "❌ NO CURSOR", "passed": False}
                
                if BACKEND == "postgres":
                    cur.execute("""
                        SELECT table_name FROM information_schema.tables 
                        WHERE table_schema = 'public'
                    """)
                else:
                    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
                
                existing = [row[0] for row in cur.fetchall()]
                found_tables = [t for t in required_tables if t in existing]
            
            missing = set(required_tables) - set(found_tables)
            
            if not missing:
                return {"status": "✅ ALL TABLES EXIST", "tables": found_tables, "passed": True}
            else:
                return {"status": f"❌ MISSING: {missing}", "found": found_tables, "passed": False}
        except Exception as e:
            return {"status": f"❌ ERROR: {e}", "passed": False}
    
    async def check_local_server(self) -> Dict[str, Any]:
        """Test 6: Local FastAPI Server Health"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                start = time.time()
                resp = await client.get(f"{LOCAL_SERVER_URL}/health")
                latency_ms = round((time.time() - start) * 1000, 2)
                
                if resp.status_code == 200:
                    data = resp.json()
                    return {"status": "✅ HEALTHY", "latency_ms": latency_ms, "db": data.get("database", "unknown"), "passed": True}
                else:
                    return {"status": f"⚠️ HTTP {resp.status_code}", "passed": False}
        except httpx.ConnectError:
            return {"status": "❌ NOT RUNNING", "passed": False, "hint": "Start server with: python core/main.py"}
        except Exception as e:
            return {"status": f"❌ ERROR: {e}", "passed": False}
    
    async def check_n8n_port(self) -> Dict[str, Any]:
        """Test 7: n8n Port Availability"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex(('localhost', 5678))
        sock.close()
        
        if result == 0:
            return {"status": "✅ PORT 5678 OPEN", "port": 5678, "passed": True}
        else:
            return {"status": "⚠️ PORT 5678 CLOSED", "passed": False, "hint": "n8n container may not be running"}
    
    async def simulate_webhook(self) -> Dict[str, Any]:
        """Test 8: Simulate Incoming WhatsApp Message (Smoke Test)"""
        try:
            # Simulated payload as n8n would transform from Evolution
            test_phone = "59100000000"  # Fake test number
            payload = {
                "phone": test_phone,
                "text": "Prueba de Sistema Natalia",
                "name": "Test User",
                "profile_pic": None,
                "fbclid": None,
                "fbp": None,
                "utm_data": {}
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                start = time.time()
                resp = await client.post(f"{LOCAL_SERVER_URL}/chat/incoming", json=payload)
                latency_ms = round((time.time() - start) * 1000, 2)
                
                if resp.status_code == 200:
                    data = resp.json()
                    return {
                        "status": "✅ PROCESSED", 
                        "latency_ms": latency_ms, 
                        "action": data.get("action"),
                        "passed": True
                    }
                else:
                    return {"status": f"❌ HTTP {resp.status_code}", "body": resp.text[:200], "passed": False}
        except httpx.ConnectError:
            return {"status": "❌ SERVER NOT RUNNING", "passed": False}
        except Exception as e:
            return {"status": f"❌ ERROR: {e}", "passed": False}

    async def run_full_audit(self):
        """Execute all checks and generate report."""
        print("\n" + "="*70)
        print("🦅 NEURAL LINK VERIFICATION PROTOCOL - Pre-Flight Check")
        print(f"   Timestamp: {datetime.now().isoformat()}")
        print("="*70 + "\n")
        
        tests = [
            ("1. Evolution API Connectivity", self.check_evolution_connectivity),
            ("2. WhatsApp Instance State", self.check_evolution_instance),
            ("3. Webhook Configuration", self.check_webhook_config),
            ("4. Database Connectivity", self.check_database),
            ("5. Database Schema", self.check_database_schema),
            ("6. Local FastAPI Server", self.check_local_server),
            ("7. n8n Port (5678)", self.check_n8n_port),
            ("8. Webhook Smoke Test", self.simulate_webhook),
        ]
        
        all_passed = True
        
        for name, test_func in tests:
            print(f"🔍 {name}...")
            result = await test_func()
            self.results[name] = result
            
            status = result.get("status", "UNKNOWN")
            print(f"   → {status}")
            
            if hint := result.get("hint"):
                print(f"   💡 Hint: {hint}")
            
            if not result.get("passed", False):
                all_passed = False
            print()
        
        # Final Verdict
        elapsed = round(time.time() - self.start_time, 2)
        print("="*70)
        if all_passed:
            print("🟢 SYSTEM STATUS: GO FOR LAUNCH")
            print("   All systems operational. Ready to deploy Natalia.")
        else:
            print("🔴 SYSTEM STATUS: NO GO")
            print("   Fix the issues above before deploying.")
        print(f"   Total audit time: {elapsed}s")
        print("="*70 + "\n")
        
        return self.results


# =================================================================
# MAIN
# =================================================================
if __name__ == "__main__":
    auditor = NeuralLinkAuditor()
    asyncio.run(auditor.run_full_audit())
