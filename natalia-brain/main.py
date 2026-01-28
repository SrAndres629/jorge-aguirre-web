from app.main import app

# Proxy file to satisfy Render's default start command (uvicorn main:app)
# This redirects the entry point to the correct location in app/main.py
