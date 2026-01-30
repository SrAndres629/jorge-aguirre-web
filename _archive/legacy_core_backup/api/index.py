# =================================================================
# API Handler for Vercel Serverless Functions
# Wraps FastAPI with Mangum for AWS Lambda/Vercel compatibility
# =================================================================
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mangum import Mangum
from main import app

# Vercel/AWS Lambda handler
handler = Mangum(app, lifespan="off")

