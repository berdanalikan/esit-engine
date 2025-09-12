"""
Vercel Handler for ESİT Technical Support AI
"""
import sys
import os
from pathlib import Path

# Add parent directory to path to import our app
sys.path.append(str(Path(__file__).parent.parent))

from app import app

# Vercel handler function
def handler(request):
    return app

# For compatibility
application = app
