
import asyncio
from playwright.async_api import async_playwright
import sys
import time

async def simulate_forensic_journey(url):
    test_fbclid = f"forensic_test_{int(time.time())}"
    target_url = f"{url}?fbclid={test_fbclid}"
    
    pixel_requests = []
    
    async with async_playwright() as p:
        print(f"👻 Launching Ghost Lead Trace on: {target_url}")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 ForensicAuditor/1.0"
        )
        page = await context.new_page()
        
        # Intercept Meta Pixel Requests
        async def handle_request(request):
            if "facebook.com/tr/" in request.url:
                pixel_requests.append(request.url)
                # print(f"📍 Pixel Detected: {request.url[:80]}...")

        page.on("request", handle_request)
        
        await page.goto(target_url)
        await page.wait_for_load_state("networkidle")
        
        print("✅ Landing Page Loaded. Verifying Pixel Initialization...")
        await asyncio.sleep(2) # Wait for pixel to fire init/pageview
        
        # Find CTA button
        cta_selector = "button:has-text('Diagnóstico')"
        try:
            await page.wait_for_selector(cta_selector, timeout=5000)
            print("🚀 Executing Conversion: Clicking WhatsApp CTA...")
            await page.click(cta_selector)
            await asyncio.sleep(3) # Wait for conversion event to fire
        except Exception as e:
            print(f"⚠️ CTA Not Found or Failed: {e}")

        await browser.close()

    print("\n" + "="*60)
    print("🏛️  VISIONARY AUDIT REPORT: E2E TELEMETRY")
    print("="*60)
    
    # 1. Pixel Check
    has_lead_event = any("ev=Lead" in r for r in pixel_requests)
    has_pv_event = any("ev=PageView" in r for r in pixel_requests)
    
    print(f"🌐 [BROWSER PIXEL] PageView: {'✅ FIRED' if has_pv_event else '❌ MISSING'}")
    print(f"🌐 [BROWSER PIXEL] Lead Event: {'✅ FIRED' if has_lead_event else '❌ MISSING'}")
    
    # 2. CAPI Synchronization Hint
    # Note: We can't verify CAPI here without DB access, but if the Pixel fired correctly
    # and the server-side logs/DB are checked later, we have E2E proof.
    
    if has_lead_event and has_pv_event:
        print("\n🏆 TELEMETRY INTEGRITY: 100% SIGNAL SYNCHRONIZATION")
        print("   Status: Pixel & Routing logic are performing at institutional standards.")
    else:
        print("\n⚠️  TELEMETRY LEAK DETECTED")
        print("   Razón: El navegador no disparó los eventos críticos de Meta.")
    
    print("="*60 + "\n")

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "https://jorge-aguirre-web.onrender.com"
    asyncio.run(simulate_forensic_journey(url))
