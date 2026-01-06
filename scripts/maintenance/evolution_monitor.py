
import asyncio
import os
import sys
import time
from datetime import datetime
import httpx
import qrcode
import io
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.live import Live
from rich.table import Table
from rich.text import Text
from rich import box

# Configuration
API_KEY = os.getenv("EVOLUTION_API_KEY", "B89599B2-37E4-4DCA-92D3-87F8674C7D69")
BASE_URL = os.getenv("EVOLUTION_API_URL", "http://evolution_api:8080")
INSTANCE_NAME = "JorgeMain"

console = Console()

class EvolutionMonitor:
    def __init__(self):
        self.layout = Layout()
        self.setup_layout()
        self.client = httpx.AsyncClient(headers={"apikey": API_KEY}, timeout=10.0)
        self.last_qr_code = None
        self.logs = []
        self.max_logs = 10
        self.is_connected = False
        self.status = "UNKNOWN"

    def setup_layout(self):
        self.layout.split(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=10)
        )
        self.layout["main"].split_row(
            Layout(name="left", ratio=1),
            Layout(name="right", ratio=1)
        )

    def generate_header(self) -> Panel:
        title = Text("🚀 EVOLUTION API CLI MONITOR", style="bold white on blue", justify="center")
        status_style = "bold green" if self.is_connected else "bold red"
        status_text = Text(f" STATUS: {self.status} ", style=status_style)
        return Panel(status_text, title=title, border_style="blue")

    def generate_qr_panel(self) -> Panel:
        if self.is_connected:
            return Panel(
                Text("\n\n📱 PHONE CONNECTED\n\n✅ Ready to receive messages", justify="center", style="bold green"),
                title="Connection Status",
                border_style="green"
            )
        
        if not self.last_qr_code:
            return Panel(Text("Fetching QR...", justify="center"), title="QR Code", border_style="yellow")

        # Convert QR to ASCII art
        qr = qrcode.QRCode(border=1)
        qr.add_data(self.last_qr_code)
        qr.make(fit=True)
        
        # Manually build ASCII QR
        qr_string = ""
        matrix = qr.get_matrix()
        for row in matrix:
            for cell in row:
                if cell:
                    qr_string += "██"  # Block for black
                else:
                    qr_string += "  "  # Space for white
            qr_string += "\n"
            
        return Panel(Text(qr_string, justify="center", style="white on black"), title="Scan this QR Code", border_style="yellow")

    def generate_logs_panel(self) -> Panel:
        table = Table(show_header=False, box=None, expand=True)
        for log in self.logs[-self.max_logs:]:
            table.add_row(log)
        return Panel(table, title="Live Event Logs", border_style="white")

    def generate_info_panel(self) -> Panel:
        grid = Table.grid(expand=True)
        grid.add_column(justify="right", style="cyan")
        grid.add_column(justify="left", style="white")
        
        grid.add_row("Instance:", INSTANCE_NAME)
        grid.add_row("API URL:", BASE_URL)
        grid.add_row("Time:", datetime.now().strftime("%H:%M:%S"))
        
        return Panel(grid, title="System Info", border_style="blue")
    
    def add_log(self, message: str, level: str = "INFO"):
        prefix = f"[{datetime.now().strftime('%H:%M:%S')}]"
        style = "white"
        if level == "ERROR": style = "red"
        if level == "SUCCESS": style = "green"
        if level == "WARN": style = "yellow"
        
        self.logs.append(Text(f"{prefix} {message}", style=style))
        if len(self.logs) > self.max_logs:
            self.logs.pop(0)

    async def check_status(self):
        try:
            # 1. Check if instance exists, if not create it
            res = await self.client.get(f"{BASE_URL}/instance/fetchInstances")
            instances = res.json()
            exists = any(i['instance']['instanceName'] == INSTANCE_NAME for i in instances)
            
            if not exists:
                self.add_log(f"Instance {INSTANCE_NAME} not found. Creating...", "WARN")
                payload = {
                    "instanceName": INSTANCE_NAME,
                    "token": "1505BD4F6F5C-42EB-B731-D6CA1643A73D", 
                    "qrcode": True,
                    "integration": "WHATSAPP-BAILEYS"
                }
                await self.client.post(f"{BASE_URL}/instance/create", json=payload)
                self.add_log("Instance created.", "SUCCESS")

            # 2. Check Connection State
            try:
                res = await self.client.get(f"{BASE_URL}/instance/connectionState/{INSTANCE_NAME}")
                state_data = res.json().get('instance', {})
                state = state_data.get('state', 'unknown')
                self.status = state.upper()

                if state == 'open':
                    self.is_connected = True
                    self.last_qr_code = None
                    self.add_log(f"Status: {state}", "SUCCESS")
                else:
                    self.is_connected = False
                    # Fetch QR if not connected
                    if state == 'close' or state == 'connecting':
                        qr_res = await self.client.get(f"{BASE_URL}/instance/connect/{INSTANCE_NAME}")
                        if qr_res.status_code == 200:
                            data = qr_res.json()
                            
                            # Prioritize 'code' (raw pairing string)
                            if 'code' in data:
                                self.last_qr_code = data['code']
                            elif 'base64' in data:
                                # Start marker check
                                b64 = data['base64']
                                if "base64," in b64:
                                    b64 = b64.split("base64,")[1]
                                # We can't render base64 image to ASCII easily here without crazy libs
                                # But usually Evolution provides 'code' too.
                                pass
            except Exception as conn_err:
                 self.add_log(f"Conn Check Failed: {conn_err}", "ERROR")

        except Exception as e:
            self.add_log(f"Global Error: {e}", "ERROR")
            self.status = "ERROR"
            self.is_connected = False

    async def update_loop(self):
        # Force a check immediately
        await self.check_status()
        
        with Live(self.layout, refresh_per_second=4, screen=True):
            while True:
                await self.check_status()
                
                # Update Layout
                self.layout["header"].update(self.generate_header())
                self.layout["left"].update(self.generate_qr_panel())
                
                # Split right panel explicitly
                right_panel = Layout()
                right_panel.split(
                    Layout(self.generate_info_panel(), size=6),
                    Layout(self.generate_logs_panel())
                )
                self.layout["main"]["right"].update(right_panel)
                
                await asyncio.sleep(2)

if __name__ == "__main__":
    monitor = EvolutionMonitor()
    try:
        asyncio.run(monitor.update_loop())
    except KeyboardInterrupt:
        print("Monitor stopped.")
