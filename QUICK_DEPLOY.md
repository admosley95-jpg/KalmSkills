# 🚀 Deploy Backend in 5 Minutes

Your frontend is live at: **https://admosley95-jpg.github.io/KalmSkills/**

To get **real job data**, deploy the backend:

## Option 1: Render.com (Easiest - FREE)

### Step 1: Sign Up
Go to https://render.com and sign up with GitHub

### Step 2: Create Web Service
1. Click "New" → "Web Service"
2. Select your KalmSkills repository
3. Fill in:
   - **Name**: `kalmskills-backend`
   - **Start Command**: 
     ```
     cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000
     ```
   - **Environment**: Free

### Step 3: Deploy & Get URL
Render will give you: `https://kalmskills-backend-xxxxx.onrender.com`

### Step 4: Update & Redeploy
Edit `.env.production`:
```
VITE_API_URL=https://kalmskills-backend-xxxxx.onrender.com
```

Commit and push:
```bash
git add .env.production
git commit -m "Update backend URL for production"
git push origin main
```

**Done!** GitHub Pages will rebuild in 1-2 minutes with real data.

---

## Test It Works
1. Go to your GitHub Pages site
2. Search for "Software Developer"
3. You should see real O*NET occupations with skills

---

**Need help?** See `BACKEND_DEPLOYMENT.md` for detailed instructions
