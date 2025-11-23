# KalmSkills Backend Services

Python services for integrating real data from open sources.

## Setup

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install requests
```

## Services

### 1. O*NET Service (`onet_service.py`)
Fetches standardized occupational data from O*NET Online.

**Usage:**
```python
from services.onet_service import OnetService

service = OnetService()

# Search for occupations
results = service.search_occupations("software developer")

# Get detailed occupation info
occupation = service.get_occupation_details("15-1252.00")

# Get skills for occupation
skills = service.get_occupation_skills("15-1252.00")

# Get technology skills
tech_skills = service.get_technology_skills("15-1252.00")
```

**API Documentation:** https://services.onetcenter.org/reference/

---

### 2. SEC Service (`sec_service.py`)
Analyzes company filings from SEC EDGAR database.

**Usage:**
```python
from services.sec_service import SECService

service = SECService()

# Search for companies
companies = service.search_companies("Tesla")

# Get company by ticker
company = service.get_company_by_ticker("TSLA")

# Analyze company health
health = service.analyze_company_health(company.cik)
print(f"Health Score: {health.health_score}/100")
print(f"Layoff Risk: {health.layoff_risk}")
```

**API Documentation:** https://www.sec.gov/edgar/sec-api-documentation

**IMPORTANT:** Must include contact email in User-Agent header per SEC requirements.

---

### 3. BLS Service (`bls_service.py`)
Fetches employment and wage statistics from Bureau of Labor Statistics.

**Setup:**
1. Register for API key at: https://data.bls.gov/registrationEngine/
2. Pass API key to service: `BLSService(api_key="YOUR_KEY")`

**Usage:**
```python
from services.bls_service import BLSService

service = BLSService(api_key="YOUR_KEY")

# Get wage data
wages = service.get_occupation_wages("15-1252")  # Software Developers
print(f"Median Hourly: ${wages.median_wage}")

# Get employment trends
trends = service.get_employment_trends("15-1252", years=5)
for trend in trends:
    print(f"{trend.year}: {trend.employment:,} (+{trend.change_percent:.1f}%)")

# Get unemployment rate
unemployment = service.get_unemployment_rate()
```

**API Documentation:** https://www.bls.gov/developers/

---

## Testing

Run individual services:
```bash
# Test O*NET
python backend/services/onet_service.py

# Test SEC
python backend/services/sec_service.py

# Test BLS (requires API key)
python backend/services/bls_service.py
```

## Next Steps

1. **Create FastAPI backend** to expose these services as REST endpoints
2. **Set up PostgreSQL** database to cache data
3. **Build ETL pipeline** for daily data updates
4. **Add Adzuna integration** for job postings
5. **Implement NLP** for SEC filing analysis

## Rate Limits

- **O*NET**: No official limit, be respectful
- **SEC**: 10 requests per second (with proper User-Agent)
- **BLS**: 
  - Without key: 25 queries/day
  - With key: 500 queries/day

## Legal Compliance

✅ All services comply with API Terms of Service
✅ Proper User-Agent headers included
✅ Attribution provided where required
✅ No scraping of restricted sites

---

See `DATA_STRATEGY.md` for complete implementation roadmap.
