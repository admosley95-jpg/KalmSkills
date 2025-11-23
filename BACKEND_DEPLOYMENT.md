# KalmSkills - Backend Deployment Guide

Your GitHub Pages frontend is now live! To use **real job data** instead of mock data, you need to deploy the backend.

## Quick Start: Deploy Backend to Render.com (Free)

### Step 1: Create Render Account
1. Go to https://render.com
2. Sign up with GitHub (recommended - auto-links your repo)

### Step 2: Create Web Service
1. Click "New +" → "Web Service"
2. Connect your GitHub repository (admosley95-jpg/KalmSkills)
3. Configure:
   - **Name**: `kalmskills-backend`
   - **Runtime**: `Python 3.11`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000`
   - **Environment**: Free tier

### Step 3: Update Configuration
After deployment, you'll get a URL like: `https://kalmskills-backend-xxxxx.onrender.com`

1. Open `.env.production` in the repo
2. Update:
   ```
   VITE_API_URL=https://kalmskills-backend-xxxxx.onrender.com
   ```
3. Commit and push - GitHub Pages will rebuild with real data!

### Step 4: Verify
- Frontend: https://admosley95-jpg.github.io/KalmSkills/
- Backend API: https://kalmskills-backend-xxxxx.onrender.com/docs

---

## Alternative: Use Local Backend

For testing locally, both frontend and backend use real data:
```powershell
.\start-local.ps1
```
- Frontend: http://localhost:5173
- Backend: http://localhost:8000

---

## Environment Variables

- **Development** (`.env.development`): `http://localhost:8000`
- **Production** (`.env.production`): Replace with your deployed backend URL

---

## Troubleshooting

**Backend won't start**: Ensure `requirements.txt` dependencies are installed
**CORS errors**: Whitelist your GitHub Pages URL in `backend/main.py`
**Blank page**: Check browser console for API connection errors

---

**Once backend is deployed, your GitHub Pages site will show real O*NET occupation data!**
