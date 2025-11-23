# URGENT: Manual Fix Required in Render Dashboard

The Procfile isn't being recognized. You must manually set the Start Command in Render.

## Immediate Action (2 minutes):

1. Go to: https://dashboard.render.com/services
2. Click the **kalmskills** service
3. Click **Settings** (top right)
4. Scroll down to **"Start Command"** field
5. Clear it completely
6. Paste this EXACTLY:
   ```
   python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT
   ```
7. Click **Save**
8. Render will auto-redeploy

## Why This Works:
- Tells Render exactly how to start the Python app
- Loads FastAPI with uvicorn
- Loads real O*NET data

## Verify:
After 2-3 minutes:
- Check: https://kalmskills-s2ko.onrender.com/docs
- You should see FastAPI Swagger docs
- Backend is running with 1,016 occupations

## Screenshot Help:
Look for **"Start Command"** field on Settings page - it's where the error message comes from.

Current broken command: `gunicorn your_application.wsgi`
New correct command: `python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
