# Complete Render Setup - Two Separate Services

The issue: Render is treating this as a Node.js project (because of package.json in root).

## Solution: Create 2 Separate Services

### Service 1: Python Backend

1. Go to https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Connect **same GitHub repo** (KalmSkills)
4. Configure:
   - **Name**: `kalmskills-backend`
   - **Environment**: `Python 3.11`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000`
   - **Plan**: Free
5. Deploy

### Service 2: Static Frontend

1. Click "New +" → "Static Site"
2. Connect **same GitHub repo**
3. Configure:
   - **Name**: `kalmskills-frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`
   - **Environment Variable**:
     - Key: `VITE_API_URL`
     - Value: (URL from backend service above)
   - **Plan**: Free
4. Deploy

---

## Alternative: Delete & Recreate Current Service

If you already have 'kalmskills' service:

1. Go to https://dashboard.render.com
2. Find 'kalmskills' service
3. Click **Settings** → **Danger Zone** → **Delete Service**
4. Follow steps above to create 2 new services

---

## After Both Services Deploy

- Backend URL: `https://kalmskills-backend.onrender.com`
- Frontend URL: `https://kalmskills-frontend.onrender.com`
- Update `.env.production` with backend URL
- Redeploy frontend

This architecture separates concerns and ensures proper runtime for each.
