
import asyncio
from playwright.async_api import async_playwright
from PIL import Image, ImageStat
import numpy as np
import sys
import os

class BalanceScanner:
    def __init__(self, url):
        self.url = url
        self.output_img = "audit_screenshot.png"

    async def scan(self):
        async with async_playwright() as p:
            print(f"👁️  Scanning Visual Balance: {self.url}")
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(viewport={"width": 1920, "height": 1080})
            await page.goto(self.url)
            await page.wait_for_load_state("networkidle")
            
            # Use a slightly longer wait for animations to settle
            await asyncio.sleep(2) 
            
            await page.screenshot(path=self.output_img, full_page=False)
            await browser.close()
            
            self.analyze_balance()

    def analyze_balance(self):
        img = Image.open(self.output_img).convert('L') # Grayscale
        data = np.array(img)
        
        # Invert: we want dark areas (text/content) to have higher weight
        inverted_data = 255 - data
        
        # Total weight
        total_mass = np.sum(inverted_data)
        if total_mass == 0:
            print("❌ Error: No visual mass detected.")
            return

        # Calculate Center of Mass (Luminance)
        h, w = inverted_data.shape
        y_indices, x_indices = np.indices((h, w))
        
        center_x = np.sum(x_indices * inverted_data) / total_mass
        center_y = np.sum(y_indices * inverted_data) / total_mass
        
        # Normalized Coordinates (-1 to 1)
        norm_x = (center_x - (w / 2)) / (w / 2)
        norm_y = (center_y - (h / 2)) / (h / 2)
        
        print("\n" + "="*50)
        print("🏛️  VISIONARY AUDIT REPORT: VISUAL BALANCE")
        print("="*50)
        print(f"📍 Center of Mass: ({center_x:.2f}, {center_y:.2f})")
        print(f"📏 Normalized Offset X: {norm_x:+.2%}")
        print(f"📏 Normalized Offset Y: {norm_y:+.2%}")
        
        if abs(norm_x) > 0.15:
            print("⚠️  ASYMMETRIC IMBALANCE DETECTED (Horizontal)")
            print("   Razón: El peso visual está muy desplazado hacia un lado.")
        else:
            print("✅ BALANCE HORIZONTAL DENTRO DEL ESTÁNDAR (±15%)")
            
        print("="*50 + "\n")
        
        # Cleanup
        # os.remove(self.output_img)

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    asyncio.run(BalanceScanner(url).scan())
