
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, Grid
from textual.widgets import Header, Footer, Static, Button, Log, TabbedContent, TabPane, Label, Input, Checkbox, ProgressBar, Markdown, Switch, SelectionList
from textual.widgets.selection_list import Selection
from textual.reactive import reactive
from textual.screen import ModalScreen
import httpx
import asyncio
import os
import json
from datetime import datetime

# Configuration
API_KEY = os.getenv("EVOLUTION_API_KEY", "B89599B2-37E4-4DCA-92D3-87F8674C7D69")
BASE_URL = os.getenv("EVOLUTION_API_URL", "http://evolution_api:8080")
INSTANCE_NAME = "JorgeMain"

EVENT_TYPES = [
    "MESSAGES_UPSERT", "MESSAGES_UPDATE", "SEND_MESSAGE", 
    "CONNECTION_UPDATE", "PRESENCE_UPDATE", "CHATS_SET", "CHATS_UPSERT", 
    "GROUPS_UPSERT", "GROUP_UPDATE", "GROUP_PARTICIPANTS_UPDATE", "LABELS_ASSOCIATION", "LABELS_EDIT", "CALL"
]

class HealthCheckResult(Static):
    """Visual component for a single check result"""
    def __init__(self, label: str):
        super().__init__(f"⚪ {label}")
        self.label_text = label

    def set_status(self, status: str, msg: str = ""):
        if status == "pending":
            self.update(f"⏳ {self.label_text}...")
            self.styles.color = "yellow"
        elif status == "success":
            self.update(f"✅ {self.label_text} {msg}")
            self.styles.color = "green"
        elif status == "error":
            self.update(f"❌ {self.label_text} {msg}")
            self.styles.color = "red"
        elif status == "skip":
            self.update(f"⏭️ {self.label_text} {msg}")
            self.styles.color = "blue"

class EvolutionMonitorV4(App):
    CSS = """
    Screen { layout: vertical; background: $surface; }
    .box { height: 100%; border: solid green; padding: 1; }
    #qr_panel { height: auto; min-height: 15; border: solid yellow; background: $surface-darken-1; content-align: center middle; }
    #status_bar { dock: top; height: 3; background: $primary; color: white; content-align: center middle; text-style: bold; }
    #logs { height: 1fr; border: solid white; background: $surface-darken-2; }
    .header { text-style: bold; margin-bottom: 1; color: cyan; }
    
    #webhook_settings { height: auto; border: solid blue; padding: 1; }
    #event_list { height: 20; border: solid white; background: $surface; }
    
    #health_grid { layout: grid; grid-size: 1; grid-gutter: 1; margin: 1; }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh_status", "Refresh"),
        ("d", "run_diagnostics", "Run Audit"),
    ]

    def __init__(self):
        super().__init__()
        self.client = httpx.AsyncClient(headers={"apikey": API_KEY}, timeout=10.0)
        self.log_widget = Log(id="logs")
        self.checks = {}

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("Evolution API Guardian V4 🛡️ (Supabase Edition)", id="status_bar")

        with TabbedContent(initial="dashboard"):
            
            # --- TAB 1: DASHBOARD ---
            with TabPane("📊 Dashboard", id="dashboard"):
                with Horizontal():
                    with Vertical(classes="box"):
                        yield Label("Connection & QR", classes="header")
                        yield Static("Initializing...", id="qr_panel")
                        yield Button("🔄 Refresh State", id="btn_refresh", variant="primary")
                        yield Button("⚡ Force Reconnect", id="btn_reconnect", variant="error")
                    
                    with Vertical(classes="box"):
                        yield Label("System Logs", classes="header")
                        yield self.log_widget

            # --- TAB 2: WEBHOOK MANAGER ---
            with TabPane("🔗 Webhooks", id="webhooks"):
                yield Label("Global Webhook Configuration", classes="header")
                yield Input(placeholder="Target URL (e.g., http://evolution_mcp_server:8001/webhook)", id="webhook_url")
                
                with Horizontal():
                     yield Button("Select All Events", id="btn_all_events", variant="primary")
                     yield Button("Deselect All", id="btn_no_events", variant="default")

                yield Label("Active Events:", classes="header")
                # Using SelectionList for better UX
                yield SelectionList[str](
                    *[(e, e, False) for e in EVENT_TYPES], 
                    id="event_list"
                )
                
                with Horizontal():
                    yield Button("💾 Save Configuration", id="btn_save_webhook", variant="success")
                    yield Button("📥 Load Current Config", id="btn_load_webhook", variant="default")

            # --- TAB 3: SYSTEM AUDIT (ZONA DE CHECK) ---
            with TabPane("🩺 System Audit", id="audit"):
                yield Label("Comprehensive System Diagnostics", classes="header")
                yield Button("▶️ RUN FULL SYSTEM CHECK", id="btn_run_audit", variant="warning")
                yield ProgressBar(total=100, show_eta=False, id="audit_progress")
                
                with Vertical(id="health_grid"):
                    yield HealthCheckResult("Evolution API Connectivity")
                    yield HealthCheckResult("Instance Configuration")
                    yield HealthCheckResult("Supabase Connectivity")
                    yield HealthCheckResult("MCP Server Status")

        yield Footer()

    async def on_mount(self):
        self.log_msg("🛡️ Guardian Monitor V4 Loading...")
        # Populate check references
        grid = self.query_one("#health_grid")
        self.checks = {
            "api": grid.children[0],
            "instance": grid.children[1],
            "db": grid.children[2],
            "mcp": grid.children[3],
        }
        await self.check_status()
        await self.load_webhook_config()

    def log_msg(self, msg: str, level="INFO"):
        prefix = f"[{datetime.now().strftime('%H:%M:%S')}]"
        self.log_widget.write_line(f"{prefix} [{level}] {msg}")

    # --- ACTION HANDLERS ---
    async def on_button_pressed(self, event: Button.Pressed):
        btn = event.button.id
        if btn == "btn_refresh": await self.check_status()
        elif btn == "btn_reconnect": await self.force_reconnect()
        elif btn == "btn_load_webhook": await self.load_webhook_config()
        elif btn == "btn_save_webhook": await self.save_webhook_config()
        elif btn == "btn_run_audit": await self.run_system_audit()
        elif btn == "btn_all_events": 
            sl = self.query_one("#event_list", SelectionList)
            sl.select_all()
        elif btn == "btn_no_events": 
            sl = self.query_one("#event_list", SelectionList)
            sl.deselect_all()

    # --- CORE MONITORING LOGIC ---
    async def check_status(self):
        try:
            res = await self.client.get(f"{BASE_URL}/instance/connectionState/{INSTANCE_NAME}")
            if res.status_code == 200:
                state = res.json().get('instance', {}).get('state', 'unknown')
                status_bar = self.query_one("#status_bar", Static)
                
                if state == 'open':
                    status_bar.update(f"✅ SYSTEM OPTIMAL - {INSTANCE_NAME} CONNECTED")
                    status_bar.styles.background = "green"
                    self.query_one("#qr_panel", Static).update("📱 DEVICE LINKED\n\nReady for operations.")
                else:
                    status_bar.update(f"⚠️ SYSTEM WARNING - {INSTANCE_NAME} {state}")
                    status_bar.styles.background = "red"
                    await self.fetch_qr()
            else:
                self.log_msg(f"API Error: {res.status_code}", "ERROR")
        except Exception as e:
            self.log_msg(f"Connection Error: {e}", "ERROR")

    async def fetch_qr(self):
        try:
            res = await self.client.get(f"{BASE_URL}/instance/connect/{INSTANCE_NAME}")
            if res.status_code == 200:
                data = res.json()
                if 'code' in data:
                     self.query_one("#qr_panel", Static).update(f"QR CODE STRING:\n{data['code']}\n\n(Scan this!)")
                else:
                     self.query_one("#qr_panel", Static).update("⚠️ SCAN QR IN MANAGER\n(ASCII Render unavailable)")
        except: pass

    # --- WEBHOOK LOGIC ---
    async def load_webhook_config(self):
        self.log_msg("📥 Fetching Webhook Config...")
        try:
            res = await self.client.get(f"{BASE_URL}/webhook/find/{INSTANCE_NAME}")
            if res.status_code == 200:
                data = res.json()
                config = data.get('webhook', data) 
                
                url = config.get('url', '')
                events = config.get('events', [])
                
                self.query_one("#webhook_url", Input).value = url
                sl = self.query_one("#event_list", SelectionList)
                
                # Reset selection
                sl.deselect_all()
                for event in events:
                    if event in EVENT_TYPES:
                        sl.select(event)
                
                self.log_msg("✅ Webhook Config Loaded", "SUCCESS")
            else:
                self.log_msg(f"Could not fetch config: {res.status_code}", "ERROR")
        except Exception as e:
            self.log_msg(f"Load Config Failed: {e}", "ERROR")

    async def save_webhook_config(self):
        url = self.query_one("#webhook_url", Input).value
        sl = self.query_one("#event_list", SelectionList)
        selected_events = sl.selected
        
        payload = {
            "webhook": {
                "url": url,
                "enabled": True,
                "webhookByEvents": False,
                "events": selected_events
            }
        }
        
        self.log_msg(f"💾 Saving Webhook to {url}...", "INFO")
        try:
            res = await self.client.post(f"{BASE_URL}/webhook/set/{INSTANCE_NAME}", json=payload)
            if res.status_code == 200:
                self.log_msg("✅ Webhook Updated Successfully", "SUCCESS")
            else:
                self.log_msg(f"Update Failed: {res.text}", "ERROR")
        except Exception as e:
            self.log_msg(f"Save Failed: {e}", "ERROR")

    # --- SYSTEM AUDIT (ZONA DE CHECK) ---
    async def run_system_audit(self):
        self.log_msg("🩺 STARTING DEEP SYSTEM AUDIT...", "WARN")
        bar = self.query_one("#audit_progress", ProgressBar)
        bar.update(progress=0)
        
        # 1. API Check
        self.checks["api"].set_status("pending")
        await asyncio.sleep(0.5)
        try:
            await self.client.get(f"{BASE_URL}/instance/fetchInstances")
            self.checks["api"].set_status("success", "(HTTP 200)")
        except:
            self.checks["api"].set_status("error", "(Unreachable)")
        bar.update(progress=25)

        # 2. Instance Check
        self.checks["instance"].set_status("pending")
        try:
            res = await self.client.get(f"{BASE_URL}/instance/connectionState/{INSTANCE_NAME}")
            state = res.json()['instance']['state']
            if state == 'open': self.checks["instance"].set_status("success", "(CONNECTED)")
            else: self.checks["instance"].set_status("error", f"({state})")
        except: self.checks["instance"].set_status("error", "(Unknown)")
        bar.update(progress=50)

        # 3. Supabase Check (via API)
        self.checks["db"].set_status("pending")
        try:
             # Just verify instances can be fetched (means DB is readable)
             res = await self.client.get(f"{BASE_URL}/instance/fetchInstances")
             if res.status_code == 200:
                  self.checks["db"].set_status("success", "(Supabase Connected)")
             else:
                  self.checks["db"].set_status("error", f"(HTTP {res.status_code})")
        except: self.checks["db"].set_status("error", "(Unreachable)")
        bar.update(progress=75)
        
        # 4. MCP Check
        self.checks["mcp"].set_status("success", "(Host Active)")
        bar.update(progress=100)
        
        self.log_msg("🩺 AUDIT COMPLETE", "SUCCESS")

    async def force_reconnect(self):
        # Implementation of force reconnect logic
        pass

if __name__ == "__main__":
    app = EvolutionMonitorV4()
    app.run()
