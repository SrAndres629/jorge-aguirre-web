
import os
import sys

# Add core to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))

from app.config import settings

print(f"🔑 Loaded Key: {settings.GOOGLE_API_KEY[:10]}...")

if settings.GOOGLE_API_KEY.startswith("AIzaSyAT"):
    print("✅ USING NEW KEY")
else:
    print("❌ USING OLD KEY (or unknown)")
