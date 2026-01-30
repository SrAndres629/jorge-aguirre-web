# =================================================================
# Vercel Serverless Handler for Jorge Aguirre Web
# Production-ready ASGI adapter using Mangum
# =================================================================
import sys
import os

# Add web directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mangum import Mangum
from main import app

# Vercel/AWS Lambda handler with lifespan disabled for serverless
handler = Mangum(app, lifespan="off")
