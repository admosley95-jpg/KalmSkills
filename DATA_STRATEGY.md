# KalmSkills Real Data Integration Strategy

## Overview
Transition from mock data to real, aggregated data from multiple open sources to create a truly intelligent career platform.

---

## 📊 Data Sources & APIs

### 1. **O*NET (Occupational Information Network)** ✅ FREE
**Source**: U.S. Department of Labor
**API**: https://services.onetcenter.org/reference/
**Data Available**:
- 1,000+ standardized occupations
- 35,000+ skill descriptors with proficiency levels
- Knowledge, Skills, Abilities (KSAs)
- Work activities, context, and values
- Technology skills by occupation
- Job zones and education requirements

**Key Endpoints**:
- `/ws/online/occupations` - List all occupations
- `/ws/online/occupations/{code}/summary` - Occupation details
- `/ws/online/occupations/{code}/skills` - Skills for occupation
- `/ws/online/search` - Search by keyword

**Implementation**:
```javascript
// Free, no API key required
fetch('https://services.onetcenter.org/ws/online/occupations/15-1252.00/skills')
```

---

### 2. **SEC EDGAR API** ✅ FREE
**Source**: U.S. Securities and Exchange Commission
**API**: https://www.sec.gov/edgar/sec-api-documentation
**Data Available**:
- Company filings (10-K, 10-Q, 8-K, etc.)
- Financial statements
- Management discussions (MD&A)
- Risk factors
- Full-text search across all filings

**Key Endpoints**:
- `https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=10-K&count=10`
- `https://data.sec.gov/submissions/CIK{cik}.json` - Company metadata
- Full-text search API coming 2025

**Implementation**:
```javascript
// Requires User-Agent header
fetch('https://data.sec.gov/submissions/CIK0001318605.json', {
  headers: { 'User-Agent': 'KalmSkills contact@kalmskills.ai' }
})
```

**NLP Extraction Strategy**:
- Parse MD&A sections for hiring language ("expanding workforce", "hiring", etc.)
- Extract risk factors mentioning layoffs
- Analyze R&D spend trends
- Track employee count changes year-over-year

---

### 3. **Burning Glass Institute (Lightcast)** 💰 PAID (Free tier limited)
**Source**: Labor market analytics
**API**: https://www.lightcast.io/open-skills-api
**Data Available**:
- Job posting data (30M+ active postings)
- Skills taxonomy (32,000+ skills)
- Real-time labor market trends
- Salary data by skill/location
- Skill clustering and relationships

**Free Alternative**:
- **Open Skills API**: https://github.com/workforce-data-initiative/skills-api
- Limited but free skills taxonomy

**Pricing**: Contact sales (typically $5k-50k/year)

---

### 4. **LinkedIn Data** ⚠️ COMPLEX
**Official API**: LinkedIn Marketing/Talent Solutions API (requires partnership)
**Alternative Methods**:
1. **Proxycurl API** (paid LinkedIn scraper): https://nubela.co/proxycurl/
   - $10/1000 requests
   - Company data, job postings, profiles

2. **RapidAPI LinkedIn Scrapers** (various providers)
   - $50-200/month for basic access

3. **Bright Data** (enterprise web scraping): https://brightdata.com/
   - Legally compliant web scraping
   - $500/month minimum

**Compliance**: Must respect LinkedIn's Terms of Service. Scraping prohibited without permission.

---

### 5. **Bureau of Labor Statistics (BLS)** ✅ FREE
**Source**: U.S. Department of Labor
**API**: https://www.bls.gov/developers/
**Data Available**:
- Employment statistics by occupation
- Wage data (median, percentiles)
- Industry employment trends
- Job outlook projections (10-year)
- CPI, unemployment rates

**Key Series IDs**:
- `OEUS000000000000015125200` - Software Developers employment
- `CES0000000001` - Total nonfarm employment

**Implementation**:
```javascript
// Free, API key required (instant approval)
fetch('https://api.bls.gov/publicAPI/v2/timeseries/data/OEUS000000000000015125200?registrationkey=YOUR_KEY')
```

---

### 6. **Indeed Job Posting API** ⚠️ RESTRICTED
**Status**: Publisher API discontinued for new users
**Alternatives**:
- **SerpApi**: https://serpapi.com/indeed-jobs-api ($50/month for 5k searches)
- **ScraperAPI + Indeed**: https://www.scraperapi.com/ ($29/month)
- **Apify Indeed Scraper**: https://apify.com/misceres/indeed-scraper ($49/month)

---

### 7. **Glassdoor API** ⚠️ RESTRICTED
**Status**: No public API
**Alternatives**:
- **Web scraping** (legal gray area, use with caution)
- **Manual data collection** for limited use cases

---

### 8. **GitHub Jobs / Stack Overflow Jobs** ❌ DISCONTINUED
**Status**: Both APIs shut down in 2021-2022
**Alternatives**:
- **Remotive API**: https://remotive.com/api (free, remote jobs)
- **GitHub Public Repos**: Analyze tech stacks via GitHub API

---

### 9. **Adzuna Job Search API** ✅ FREE (with attribution)
**API**: https://developer.adzuna.com/
**Data Available**:
- 10M+ job postings globally
- Salary data and trends
- Job category taxonomy
- Historical data

**Free Tier**: 1000 calls/month
**Requirement**: Display "powered by Adzuna" logo

---

### 10. **USAJobs API** ✅ FREE
**Source**: Federal government jobs
**API**: https://developer.usajobs.gov/
**Data Available**:
- Federal job postings
- Salary ranges
- Required skills and qualifications

---

## 🏗️ Proposed Architecture

### Phase 1: Core Free Data (Immediate)
```
KalmSkills Backend
├── O*NET Integration (Skills Taxonomy)
│   └── 35k+ standardized skills
├── SEC EDGAR Integration (Company Health)
│   └── Financial data, hiring signals
├── BLS Integration (Salary & Employment Stats)
│   └── Real wage data by occupation
└── Adzuna Integration (Job Postings)
    └── 10M+ job listings with attribution
```

### Phase 2: Enhanced Data (Next 3 months)
```
├── Proxycurl/RapidAPI (LinkedIn insights)
├── SerpApi (Indeed job scraping)
└── Custom web scraping (compliance-focused)
```

### Phase 3: Premium Data (6+ months)
```
├── Lightcast/Burning Glass partnership
└── Direct partnerships with job boards
```

---

## 💻 Technical Implementation Plan

### Backend Architecture (Recommended: Python + FastAPI)

```
kalmskills-backend/
├── services/
│   ├── onet_service.py          # O*NET API integration
│   ├── sec_service.py           # SEC EDGAR parsing
│   ├── bls_service.py           # BLS statistics
│   ├── adzuna_service.py        # Job postings
│   └── nlp_service.py           # Text analysis (spaCy/transformers)
├── database/
│   ├── postgres/                # Structured data
│   ├── elasticsearch/           # Full-text search
│   └── redis/                   # Caching
├── scrapers/                    # Ethical web scrapers
├── ml_models/
│   ├── skill_extractor/         # NER model for skills
│   ├── company_analyzer/        # SEC text analysis
│   └── salary_predictor/        # ML-based salary estimation
└── api/
    └── fastapi_app.py           # REST API for frontend
```

### Data Pipeline

```mermaid
[O*NET API] ──┐
[SEC EDGAR]  ──┼──> [ETL Pipeline] ──> [PostgreSQL] ──┐
[BLS API]    ──┤                                       ├──> [API] ──> [React Frontend]
[Adzuna API] ──┘                                       │
                                                       └──> [Elasticsearch]
                    ↓
              [Nightly Sync Jobs]
```

---

## 📝 Implementation Steps

### Step 1: Set Up Backend (Week 1-2)
1. Create FastAPI backend
2. Set up PostgreSQL database
3. Implement O*NET service
4. Create skill taxonomy tables

### Step 2: Company Intelligence (Week 3-4)
1. Implement SEC EDGAR service
2. Build NLP pipeline for 10-K analysis
3. Extract hiring signals
4. Calculate company health scores

### Step 3: Job Aggregation (Week 5-6)
1. Integrate Adzuna API
2. Implement job scraping (ethical/legal methods)
3. Build job matching algorithm
4. Create caching layer

### Step 4: Salary & Trends (Week 7-8)
1. Integrate BLS API
2. Build salary prediction model
3. Calculate skill demand trends
4. Create market intelligence dashboard

---

## 🔑 API Keys Needed (All Free to Start)

1. **O*NET**: None required (open access)
2. **SEC EDGAR**: None required (rate limit: 10 req/sec with User-Agent)
3. **BLS**: Register at https://data.bls.gov/registrationEngine/ (instant)
4. **Adzuna**: Register at https://developer.adzuna.com/
5. **USAJobs**: Register at https://developer.usajobs.gov/

---

## 📊 Database Schema (PostgreSQL)

```sql
-- Skills Taxonomy (from O*NET)
CREATE TABLE skills (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    onet_code VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Companies (from SEC)
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    cik VARCHAR(20) UNIQUE,
    ticker VARCHAR(10),
    industry VARCHAR(100),
    employee_count INTEGER,
    last_10k_date DATE,
    health_score INTEGER,
    layoff_risk VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Jobs (aggregated from multiple sources)
CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    company_id INTEGER REFERENCES companies(id),
    description TEXT,
    salary_min DECIMAL(10,2),
    salary_max DECIMAL(10,2),
    location VARCHAR(255),
    source VARCHAR(50),
    external_id VARCHAR(255),
    posted_date DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Job Skills (many-to-many)
CREATE TABLE job_skills (
    job_id INTEGER REFERENCES jobs(id),
    skill_id VARCHAR(50) REFERENCES skills(id),
    required BOOLEAN DEFAULT true,
    proficiency_level VARCHAR(50),
    PRIMARY KEY (job_id, skill_id)
);

-- Market Trends
CREATE TABLE skill_trends (
    skill_id VARCHAR(50) REFERENCES skills(id),
    date DATE,
    demand_score DECIMAL(5,2),
    avg_salary DECIMAL(10,2),
    job_count INTEGER,
    PRIMARY KEY (skill_id, date)
);
```

---

## ⚖️ Legal & Compliance

### Must-Have:
1. **SEC User-Agent**: Include company name + contact email
2. **Adzuna Attribution**: Display "powered by Adzuna" logo
3. **BLS Citation**: Credit Bureau of Labor Statistics
4. **robots.txt Compliance**: Respect all robots.txt files
5. **Rate Limiting**: Stay within API limits (implement exponential backoff)
6. **Data Privacy**: No PII collection without consent
7. **Terms of Service**: Review all API ToS before use

### Avoid:
- LinkedIn scraping without permission
- Indeed scraping (use official alternatives)
- Any method violating CFAA (Computer Fraud and Abuse Act)

---

## 💰 Estimated Costs (Monthly)

### Free Tier (Months 1-3)
- O*NET: $0
- SEC EDGAR: $0
- BLS: $0
- Adzuna: $0 (1000 calls/month)
- Hosting (AWS/Vercel): $50-100
- **Total: $50-100/month**

### Growth Tier (Months 4-12)
- Add Proxycurl: $99/month
- Add SerpApi: $50/month
- Upgraded hosting: $200/month
- **Total: ~$350/month**

### Enterprise Tier (Year 2+)
- Lightcast API: $15k-50k/year
- Advanced infrastructure: $1k/month
- **Total: ~$2k-5k/month**

---

## 🚀 Quick Start Commands

```bash
# Install backend dependencies
pip install fastapi uvicorn sqlalchemy psycopg2 requests beautifulsoup4 spacy

# Get O*NET data
curl https://services.onetcenter.org/ws/online/occupations/15-1252.00

# Get SEC data
curl -H "User-Agent: KalmSkills/1.0 (contact@kalmskills.ai)" \
  https://data.sec.gov/submissions/CIK0001318605.json

# Get BLS data (need API key)
curl "https://api.bls.gov/publicAPI/v2/timeseries/data/OEUS000000000000015125200?registrationkey=YOUR_KEY"
```

---

## 📈 Success Metrics

- **Skills Coverage**: 30,000+ O*NET skills integrated
- **Company Coverage**: 5,000+ public companies tracked
- **Job Listings**: 100,000+ active jobs
- **Data Freshness**: Daily updates for jobs, weekly for company data
- **API Uptime**: 99.9%

---

## Next Steps

Would you like me to:
1. ✅ Create the backend API structure (FastAPI + Python)
2. ✅ Build the O*NET integration service
3. ✅ Build the SEC EDGAR scraper
4. ✅ Set up the database schema
5. ✅ Create ETL pipeline for data aggregation

Let me know which component to build first!
