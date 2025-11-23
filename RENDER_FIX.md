# Fix Render Deployment - Backend Configuration Issue

Your Render backend is deployed with the wrong runtime. Here's how to fix it:

## Problem
Render was set to Node.js runtime but we need Python 3.11 for the backend

## Solution

### Option 1: Fix via Render Dashboard (Recommended)

1. Go to your service at https://dashboard.render.com
2. Find your **kalmskills** service
3. Click **Settings**
4. Scroll to **Build & Deploy**
5. Change:
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000`
6. Redeploy

### Option 2: Use render.yaml Blueprint

The `render.yaml` file in the repo defines proper configuration for both frontend and backend.

1. Delete current services
2. Create new "Blueprint" deployment
3. Select "render.yaml" 
4. Deploy

---

## Quick Start After Fix

Once backend is running:
- Backend API: https://kalmskills.onrender.com
- Check API: https://kalmskills.onrender.com/docs
- Frontend will auto-connect and show real data

