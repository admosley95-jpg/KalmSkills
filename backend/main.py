"""
KalmSkills Backend - FastAPI Server
Provides REST API endpoints for React frontend
NO API KEYS REQUIRED - Uses free public APIs
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel
import logging

from services.onet_service import OnetService, Skill, Occupation
from services.sec_service import SECService, CompanyHealth
from services.bls_service import BLSService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="KalmSkills API",
    description="Career Intelligence Platform - Aggregates skills, jobs, and company data",
    version="1.0.0"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://192.168.1.18:5173",
        "https://admosley95-jpg.github.io"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services (NO API KEYS NEEDED)
onet_service = OnetService()
sec_service = SECService()
bls_service = BLSService()  # Works without key (25 queries/day)

# Pydantic models for API responses
class SkillResponse(BaseModel):
    id: str
    name: str
    description: str
    category: str
    level: Optional[float] = None
    importance: Optional[float] = None
    demand_percent: Optional[float] = None
    avg_salary: Optional[float] = None
    trend: Optional[str] = None

class OccupationResponse(BaseModel):
    code: str
    title: str
    description: str
    skills: List[SkillResponse]
    education_level: str
    median_salary: Optional[float] = None

class CompanyHealthResponse(BaseModel):
    name: str
    ticker: Optional[str]
    health_score: int
    layoff_risk: str
    hiring_trend: str
    funding_status: str
    sentiment: str
    signal: str

class JobMatchResponse(BaseModel):
    occupation_code: str
    occupation_title: str
    match_score: int
    matched_skills: List[str]
    missing_skills: List[str]
    salary_range: str

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "KalmSkills API v1.0",
        "status": "online",
        "docs": "/docs",
        "services": {
            "onet": "✅ Active (no key required)",
            "sec": "✅ Active (no key required)",
            "bls": "✅ Active (limited to 25 queries/day without key)"
        }
    }

# O*NET Endpoints
@app.get("/api/occupations/search")
async def search_occupations(q: str, limit: int = 10):
    """Search for occupations by keyword"""
    try:
        results = onet_service.search_occupations(q)
        return {
            "query": q,
            "count": len(results[:limit]),
            "results": results[:limit]
        }
    except Exception as e:
        logger.error(f"Error searching occupations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/occupations/{onet_code}")
async def get_occupation(onet_code: str):
    """Get detailed information about an occupation"""
    try:
        occupation = onet_service.get_occupation_details(onet_code)
        if not occupation:
            raise HTTPException(status_code=404, detail="Occupation not found")
        
        return {
            "code": occupation.code,
            "title": occupation.title,
            "description": occupation.description,
            "education_level": occupation.education_level,
            "skills": [
                {
                    "id": skill.id,
                    "name": skill.name,
                    "description": skill.description,
                    "level": skill.level,
                    "importance": skill.importance
                }
                for skill in occupation.skills
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching occupation {onet_code}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/occupations/{onet_code}/skills")
async def get_occupation_skills(onet_code: str):
    """Get skills required for an occupation"""
    try:
        skills = onet_service.get_occupation_skills(onet_code)
        return {
            "occupation_code": onet_code,
            "count": len(skills),
            "skills": [
                {
                    "id": skill.id,
                    "name": skill.name,
                    "description": skill.description,
                    "level": skill.level,
                    "importance": skill.importance,
                    "category": skill.category
                }
                for skill in skills
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching skills: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/occupations/{onet_code}/technology")
async def get_technology_skills(onet_code: str):
    """Get technology/tool skills for an occupation"""
    try:
        tech_skills = onet_service.get_technology_skills(onet_code)
        return {
            "occupation_code": onet_code,
            "count": len(tech_skills),
            "technologies": tech_skills
        }
    except Exception as e:
        logger.error(f"Error fetching technology skills: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# SEC Endpoints
@app.get("/api/companies/search")
async def search_companies(q: str, limit: int = 10):
    """Search for companies by name"""
    try:
        companies = sec_service.search_companies(q, limit)
        return {
            "query": q,
            "count": len(companies),
            "results": [
                {
                    "cik": c.cik,
                    "name": c.name,
                    "ticker": c.ticker,
                    "industry": c.industry
                }
                for c in companies
            ]
        }
    except Exception as e:
        logger.error(f"Error searching companies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/companies/ticker/{ticker}")
async def get_company_by_ticker(ticker: str):
    """Get company information by stock ticker"""
    try:
        company = sec_service.get_company_by_ticker(ticker)
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        return {
            "cik": company.cik,
            "name": company.name,
            "ticker": company.ticker,
            "industry": company.industry,
            "sic": company.sic
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching company: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/companies/{cik}/health")
async def get_company_health(cik: str):
    """Analyze company health based on SEC filings"""
    try:
        health = sec_service.analyze_company_health(cik)
        if not health:
            raise HTTPException(status_code=404, detail="Company data not found")
        
        return {
            "name": health.company.name,
            "ticker": health.company.ticker,
            "industry": health.company.industry,
            "health_score": health.health_score,
            "layoff_risk": health.layoff_risk,
            "hiring_trend": health.hiring_trend,
            "funding_status": health.funding_status,
            "sentiment": health.sentiment,
            "signal": health.signal
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing company health: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# BLS Endpoints (works without key, limited to 25 queries/day)
@app.get("/api/wages/{occupation_code}")
async def get_wages(occupation_code: str):
    """Get wage data for an occupation (BLS)"""
    try:
        wages = bls_service.get_occupation_wages(occupation_code)
        if not wages:
            raise HTTPException(status_code=404, detail="Wage data not found")
        
        annual_salary = wages.median_wage * 2080  # Convert hourly to annual
        
        return {
            "occupation_code": wages.occupation_code,
            "occupation_title": wages.occupation_title,
            "median_hourly": wages.median_wage,
            "median_annual": round(annual_salary, 2),
            "note": "Using BLS API without key (25 queries/day limit)"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching wage data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/unemployment")
async def get_unemployment():
    """Get current national unemployment rate"""
    try:
        rate = bls_service.get_unemployment_rate()
        if rate is None:
            raise HTTPException(status_code=503, detail="Unable to fetch unemployment data")
        
        return {
            "unemployment_rate": rate,
            "note": "National unemployment rate from BLS"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching unemployment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Pydantic model for match request
class MatchRequest(BaseModel):
    resume_skills: List[str]
    target_occupation: Optional[str] = None

# Resume Matching Endpoint
@app.post("/api/match")
async def match_resume(request: MatchRequest):
    """
    Match resume skills against target occupation
    
    Args:
        request: MatchRequest with resume_skills and optional target_occupation
    """
    resume_skills = request.resume_skills
    target_occupation = request.target_occupation
    try:
        # If no target specified, search for best match
        if not target_occupation:
            # Simple keyword matching - could be enhanced with NLP
            search_query = " ".join(resume_skills[:3])
            occupations = onet_service.search_occupations(search_query)
            if not occupations:
                raise HTTPException(status_code=404, detail="No matching occupations found")
            target_occupation = occupations[0]['code']
        
        # Get required skills for occupation
        required_skills = onet_service.get_occupation_skills(target_occupation)
        required_skill_names = {skill.name.lower() for skill in required_skills}
        resume_skill_names = {skill.lower() for skill in resume_skills}
        
        # Calculate match
        matched = list(resume_skill_names & required_skill_names)
        missing = list(required_skill_names - resume_skill_names)
        
        match_score = int((len(matched) / len(required_skill_names)) * 100) if required_skill_names else 0
        
        # Get occupation details
        occupation = onet_service.get_occupation_details(target_occupation)
        
        return {
            "occupation_code": target_occupation,
            "occupation_title": occupation.title if occupation else "Unknown",
            "match_score": match_score,
            "matched_skills": matched,
            "missing_skills": missing[:10],  # Limit to top 10
            "recommendation": "Strong match" if match_score >= 70 else "Consider upskilling" if match_score >= 40 else "Significant skill gap"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error matching resume: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Run with: uvicorn main:app --reload --host 0.0.0.0 --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
