#!/usr/bin/env python3
"""
Render Entry Point - FastAPI Application
"""
import os
import sys

# Add backend to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.main import app

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get('PORT', 8000))
    uvicorn.run(
        app,
        host='0.0.0.0',
        port=port,
        reload=False
    )

# For Gunicorn/WSGI compatibility (if Procfile fails)
application = app

