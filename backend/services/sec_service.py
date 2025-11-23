"""
KalmSkills Backend - SEC EDGAR Integration Service
Fetches and analyzes company filings from SEC EDGAR
"""

import requests
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CompanyInfo:
    cik: str
    name: str
    ticker: Optional[str]
    sic: str
    industry: str
    employee_count: Optional[int] = None

@dataclass
class CompanyHealth:
    company: CompanyInfo
    health_score: int
    layoff_risk: str  # Low, Medium, High
    hiring_trend: str  # e.g., "+35% YoY"
    funding_status: str
    sentiment: str
    signal: str

class SECService:
    """Service for interacting with SEC EDGAR database"""

    BASE_URL = "https://data.sec.gov"
    CONTACT_EMAIL = "contact@kalmskills.ai"  # REQUIRED by SEC

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': f'KalmSkills/1.0 ({self.CONTACT_EMAIL})',
            'Accept': 'application/json'
        })

    def get_company_by_ticker(self, ticker: str) -> Optional[CompanyInfo]:
        """Get company information by stock ticker"""
        try:
            # Updated SEC API endpoint
            url = f"{self.BASE_URL}/files/company_tickers_exchange.json"
            response = self.session.get(url)

            # If that fails, try the older endpoint
            if response.status_code == 404:
                url = "https://www.sec.gov/files/company_tickers.json"
                response = self.session.get(url)

            response.raise_for_status()

            companies = response.json()
            for company_data in companies.values():
                if company_data.get('ticker', '').upper() == ticker.upper():
                    return self._parse_company_info(company_data)

            return None
        except requests.RequestException as e:
            logger.error(f"Error fetching company for ticker {ticker}: {e}")
            return None

    def get_company_submissions(self, cik: str) -> Dict:
        """Get all submissions/filings for a company"""
        try:
            # Pad CIK to 10 digits
            cik_padded = cik.zfill(10)
            url = f"{self.BASE_URL}/submissions/CIK{cik_padded}.json"

            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching submissions for CIK {cik}: {e}")
            return {}

    def get_latest_10k(self, cik: str) -> Optional[str]:
        """Get the latest 10-K filing URL for a company"""
        submissions = self.get_company_submissions(cik)
        filings = submissions.get('filings', {}).get('recent', {})

        forms = filings.get('form', [])
        accession_numbers = filings.get('accessionNumber', [])

        for i, form in enumerate(forms):
            if form == '10-K':
                accession = accession_numbers[i].replace('-', '')
                # Construct document URL
                url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/{accession_numbers[i]}-index.htm"
                return url

        return None

    def analyze_company_health(self, cik: str) -> Optional[CompanyHealth]:
        """Analyze company health based on SEC filings"""
        try:
            submissions = self.get_company_submissions(cik)

            company_info = CompanyInfo(
                cik=cik,
                name=submissions.get('name', ''),
                ticker=submissions.get('tickers', [''])[0] if submissions.get('tickers') else None,
                sic=submissions.get('sic', ''),
                industry=submissions.get('sicDescription', ''),
                employee_count=self._extract_employee_count(submissions)
            )

            # Analyze filings for signals
            health_metrics = self._analyze_filings(submissions)

            return CompanyHealth(
                company=company_info,
                health_score=health_metrics['health_score'],
                layoff_risk=health_metrics['layoff_risk'],
                hiring_trend=health_metrics['hiring_trend'],
                funding_status=health_metrics['funding_status'],
                sentiment=health_metrics['sentiment'],
                signal=health_metrics['signal']
            )
        except Exception as e:
            logger.error(f"Error analyzing company health for CIK {cik}: {e}")
            return None

    def _parse_company_info(self, data: Dict) -> CompanyInfo:
        """Parse company info from SEC data"""
        return CompanyInfo(
            cik=str(data.get('cik_str', '')),
            name=data.get('title', ''),
            ticker=data.get('ticker', ''),
            sic=str(data.get('sic', '')),
            industry=''  # Would need SIC code lookup
        )

    def _extract_employee_count(self, submissions: Dict) -> Optional[int]:
        """Extract employee count from company data"""
        # This would require parsing actual filing documents
        # For now, return None - would need full text parsing
        return None

    def _analyze_filings(self, submissions: Dict) -> Dict:
        """Analyze recent filings to determine company health"""
        # Simplified analysis - in production, would parse actual filing text
        # using NLP to detect hiring language, risk factors, etc.

        filings = submissions.get('filings', {}).get('recent', {})
        recent_forms = filings.get('form', [])

        # Check for 8-K (material events - often includes layoffs)
        has_recent_8k = '8-K' in recent_forms[:5]

        # Count recent filings as proxy for company activity
        recent_10k_count = recent_forms[:10].count('10-K')

        # Simple heuristic scoring
        health_score = 75  # Base score
        layoff_risk = "Low"
        sentiment = "Stable"
        hiring_trend = "+5% YoY"
        funding_status = "Public"
        signal = "Regular filing activity observed."

        if has_recent_8k:
            health_score -= 10
            layoff_risk = "Medium"
            sentiment = "Cautionary"
            signal = "Recent 8-K filing may indicate material changes."

        if recent_10k_count == 0:
            health_score -= 20
            signal = "No recent 10-K filings found."

        return {
            'health_score': health_score,
            'layoff_risk': layoff_risk,
            'hiring_trend': hiring_trend,
            'funding_status': funding_status,
            'sentiment': sentiment,
            'signal': signal
        }

    def search_companies(self, query: str, limit: int = 10) -> List[CompanyInfo]:
        """Search for companies by name"""
        try:
            # Updated SEC API endpoint
            url = f"{self.BASE_URL}/files/company_tickers_exchange.json"
            response = self.session.get(url)

            # If that fails, try the older endpoint
            if response.status_code == 404:
                url = "https://www.sec.gov/files/company_tickers.json"
                response = self.session.get(url)

            response.raise_for_status()

            companies = response.json()
            results = []

            query_lower = query.lower()
            for company_data in companies.values():
                if query_lower in company_data.get('title', '').lower():
                    results.append(self._parse_company_info(company_data))
                    if len(results) >= limit:
                        break

            return results
        except requests.RequestException as e:
            logger.error(f"Error searching companies: {e}")
            return []


# Example usage
if __name__ == "__main__":
    service = SECService()

    # Search for a company
    print("Searching for 'Tesla'...")
    companies = service.search_companies("Tesla", limit=5)

    for company in companies:
        print(f"\n{company.name} ({company.ticker})")
        print(f"CIK: {company.cik}")

        # Analyze company health
        print("\nAnalyzing company health...")
        health = service.analyze_company_health(company.cik)

        if health:
            print(f"Health Score: {health.health_score}/100")
            print(f"Layoff Risk: {health.layoff_risk}")
            print(f"Sentiment: {health.sentiment}")
            print(f"Signal: {health.signal}")

        break  # Just analyze first result
