import uvicorn
from fastapi import FastAPI, Request
from datetime import datetime
import json
import os

app = FastAPI(title="Evolution API Webhook Listener (Senior Suite)")

# Color codes for terminal output
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"

@app.post("/webhook")
async def handle_webhook(request: Request):
    try:
        payload = await request.json()
        event_type = payload.get("event", "UNKNOWN_EVENT")
        instance = payload.get("instance", "unknown")
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        print(f"\n{BLUE}[{timestamp}] 📥 EVENT RECEIVED: {YELLOW}{event_type}{RESET}")
        print(f"{BLUE}Instance:{RESET} {instance}")
        
        # Log payload snippet
        print(f"{BLUE}Payload Detail:{RESET}")
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        print("-" * 50)
        
        return {"status": "success", "message": "Event logged"}
    except Exception as e:
        print(f"{RED}Error parsing webhook: {e}{RESET}")
        return {"status": "error", "message": str(e)}

@app.get("/health")
async def health():
    return {"status": "online", "timestamp": datetime.now()}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8081))
    print(f"{GREEN}🚀 Starting Webhook Listener on port {port}...{RESET}")
    print(f"{YELLOW}Configure your Evolution API to point to this URL/webhook{RESET}")
    uvicorn.run(app, host="0.0.0.0", port=port)
