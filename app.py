#!/usr/bin/env python3
"""
Render Entry Point - Start Backend Server
"""
import os
import sys

# Add backend to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

if __name__ == "__main__":
    from backend.main import app
    import uvicorn
    
    port = int(os.environ.get('PORT', 8000))
    uvicorn.run(
        "backend.main:app",
        host='0.0.0.0',
        port=port,
        reload=False
    )

