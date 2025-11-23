# API Keys Guide for KalmSkills

## Summary: What You Need (and Don't Need)

### ✅ NO API KEY NEEDED (Immediately Available)
- **O*NET Web Services** - FREE, no registration required
- **SEC EDGAR** - FREE, no key needed (just proper User-Agent header)

### 🔑 FREE API KEY (Quick Registration)
- **BLS (Bureau of Labor Statistics)** - FREE, register at https://data.bls.gov/registrationEngine/
  - Without key: 25 queries/day (sufficient for testing)
  - With key: 500 queries/day
  - Registration takes 2 minutes

### 💰 PAID API KEYS (Can Skip for Now)
- **Adzuna** - FREE tier: 1000 calls/month, register at https://developer.adzuna.com/
- **Proxycurl (LinkedIn)** - $300/month (10,000 credits)
- **SerpApi (Google/Indeed)** - $50/month (5,000 searches)
- **Lightcast (Burning Glass)** - Enterprise pricing only

---

## Quick Start: No Keys Required

You can start immediately with:
1. **O*NET** - 35,000+ standardized skills, occupation data
2. **SEC EDGAR** - Company financial intelligence
3. **BLS (limited)** - 25 queries/day without key

This gives you 90% of the core functionality!

---

## Registration Links

### Free & Recommended

**BLS API Key** (2 minutes)
- Register: https://data.bls.gov/registrationEngine/
- Increases limit from 25 to 500 queries/day
- Required fields: Name, email, organization
- Key delivered via email instantly

**Adzuna API Key** (5 minutes)
- Register: https://developer.adzuna.com/signup
- FREE tier: 1,000 job searches/month
- Required: Email verification
- Good for job posting aggregation

### Optional (Can Add Later)

**Proxycurl** - For LinkedIn profile data
- Signup: https://nubela.co/proxycurl/
- $300/month minimum
- Skip for MVP - use O*NET instead

**SerpApi** - For Google/Indeed job scraping
- Signup: https://serpapi.com/users/sign_up
- $50/month for 5,000 searches
- Skip for MVP - use Adzuna free tier

---

## Environment Variables Setup

Create `.env` file in backend directory:

```bash
# Required for production (but works without)
BLS_API_KEY=your_bls_key_here

# Optional - add when ready
ADZUNA_APP_ID=your_adzuna_app_id
ADZUNA_API_KEY=your_adzuna_key

# Not needed for MVP
# PROXYCURL_API_KEY=skip_for_now
# SERPAPI_KEY=skip_for_now
```

---

## Cost Breakdown

### Free Tier (MVP)
- O*NET: FREE ✅
- SEC EDGAR: FREE ✅
- BLS (with key): FREE ✅
- Adzuna (1k calls/month): FREE ✅
- **Total: $0/month**

### Growth Tier
- Above + Adzuna Premium: $50/month
- Above + SerpApi: $50/month
- **Total: ~$100/month**

### Enterprise Tier
- Above + Proxycurl: $300/month
- Above + Lightcast: $2,000+/month
- **Total: $2,500+/month**

---

## Recommendation

**Start with FREE tier (no keys needed):**
1. O*NET for skills taxonomy ✅
2. SEC EDGAR for company intelligence ✅
3. BLS without key (25 queries/day) ✅

**After testing, add:**
1. BLS API key (free, 2-min registration)
2. Adzuna API key (free tier, 5-min registration)

**Skip entirely for MVP:**
- Proxycurl (LinkedIn)
- SerpApi (Google/Indeed)
- Lightcast (Burning Glass)

This gets you 90% of the functionality at $0 cost!
