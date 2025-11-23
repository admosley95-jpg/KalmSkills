"""
WSGI Application Entry Point for Production Deployment
Used by Gunicorn on Render.com or similar services
"""
from backend.main import app

if __name__ == "__main__":
    app.run()
