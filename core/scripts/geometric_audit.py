
import asyncio
import json
from playwright.async_api import async_playwright
import sys

class GeometricAuditor:
    def __init__(self, url):
        self.url = url
        self.results = []

    async def run_audit(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080}
            )
            page = await context.new_page()
            
            print(f"🚀 Launching Visionary Auditor on: {self.url}")
            await page.goto(self.url)
            await page.wait_for_load_state("networkidle")

            # 📏 1. HERO SECTION ALIGNMENT
            hero_audit = await self.audit_hero(page)
            self.results.append(hero_audit)

            # 📏 2. SECTION CENTERING (General Grid Audit)
            grid_audit = await self.audit_grid(page)
            self.results.append(grid_audit)

            await browser.close()
            self.report()

    async def audit_hero(self, page):
        """
        GEOMETRICAL AUDIT: Hero Section
        Checks if the '30 Años' block and the main name are optically centered.
        """
        # Selector for the hero text container
        hero_text_selector = "h1" 
        
        # Get bounding box
        box = await page.locator(hero_text_selector).bounding_box()
        viewport_width = page.viewport_size["width"]
        
        if not box:
            return {"component": "Hero", "status": "FAIL", "reason": "H1 not found"}

        # Calculate Offset from center
        actual_center = box["x"] + (box["width"] / 2)
        ideal_center = viewport_width / 2
        offset = actual_center - ideal_center
        
        status = "PASS" if abs(offset) < 5 else "FAIL"
        
        return {
            "component": "Hero Positioning",
            "status": status,
            "metric": "Horizontal Offset",
            "value": f"{offset:.2f}px",
            "threshold": "5px",
            "metadata": {"box": box}
        }

    async def audit_grid(self, page):
        """
        GEOMETRICAL AUDIT: Container Grid Consistency
        Checks if all 'container' classes have the same width and X position.
        """
        containers = await page.eval_on_selector_all(".container", """
            elements => elements.map(el => {
                const rect = el.getBoundingClientRect();
                return { x: rect.x, width: rect.width };
            })
        """)

        if not containers:
            return {"component": "Grid Integrity", "status": "FAIL", "reason": "No containers found"}

        widths = [c['width'] for c in containers]
        xs = [c['x'] for c in containers]
        
        width_variance = max(widths) - min(widths)
        x_variance = max(xs) - min(xs)
        
        status = "PASS" if width_variance < 2 and x_variance < 2 else "FAIL"
        
        return {
            "component": "Grid Integrity",
            "status": status,
            "metrics": {
                "width_variance": f"{width_variance:.2f}px",
                "x_variance": f"{x_variance:.2f}px"
            },
            "threshold": "2px"
        }

    def report(self):
        print("\n" + "="*50)
        print("🏛️  VISIONARY AUDIT REPORT: GEOMETRIC INTEGRITY")
        print("="*50)
        for res in self.results:
            status_emoji = "✅" if res['status'] == "PASS" else "❌"
            print(f"{status_emoji} {res['component']}: {res['status']}")
            if 'metrics' in res:
                for k, v in res['metrics'].items():
                    print(f"   ∟ {k}: {v}")
            if 'value' in res:
                print(f"   ∟ metric: {res['value']}")
        print("="*50 + "\n")

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    asyncio.run(GeometricAuditor(url).run_audit())
