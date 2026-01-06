# 🤖 Keep-Alive Bot Audit
**Date**: 2026-01-06
**Topic**: Impact of "Keep-Alive" bots on Meta Tracking Costs

## ❓ The Concern
"I have a bot that visits my website every few minutes to prevent Render from sleeping. Does this inflate my ad costs or mess up my tracking?"

## 🔍 Techncial Analysis
1.  **Pixel Impact (Browser Tracking)**:
    -   **Status**: ✅ SAFE.
    -   **Reason**: Bots (like UptimeRobot or Cron jobs) normally just fetch the HTML code. They **do not execute JavaScript**. Since the Meta Pixel is a JavaScript snippet, it never loads. No `PageView` is sent.

2.  **CAPI Impact (Server Tracking)**:
    -   **Status**: ✅ SAFE.
    -   **Reason**: Your backend (`main.py`) controls CAPI. It serves the HTML to the bot but does **not** fire a CAPI event for simple page loads (GET requests). CAPI is only triggered when the Frontend specifically sends a POST request (which the bot won't do).

3.  **Cost Impact**:
    -   **Status**: ✅ $0.00.
    -   **Reason**: No events fired = No data sent to Meta = No attribution costs.

## 💡 Recommendation
Your current setup is fine. To make it even "cleaner" and save a tiny bit of server CPU:
-   **Best Practice**: Point your bot to `https://jorgeaguirreflores.com/health` instead of the home page.
-   **Why?**: The `/health` endpoint is designed to say "I'm alive" without loading the full website database/templates. It's faster and lighter.

---
*Signed,*
*Agent AntiGravity*
