"""
KalmSkills Backend - Bureau of Labor Statistics Integration
Fetches employment and wage data from BLS API
"""

import requests
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class WageData:
    occupation_code: str
    occupation_title: str
    median_wage: float
    mean_wage: float
    percentile_10: Optional[float] = None
    percentile_25: Optional[float] = None
    percentile_75: Optional[float] = None
    percentile_90: Optional[float] = None
    total_employment: Optional[int] = None

@dataclass
class EmploymentTrend:
    occupation_code: str
    year: int
    employment: int
    change_percent: Optional[float] = None

class BLSService:
    """Service for interacting with Bureau of Labor Statistics API"""

    BASE_URL = "https://api.bls.gov/publicAPI/v2"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize BLS Service

        Args:
            api_key: BLS API key (register at https://data.bls.gov/registrationEngine/)
                    Without key: 25 queries per day, 10 years of data
                    With key: 500 queries per day, 20 years of data
        """
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })

    def get_timeseries_data(self, series_ids: List[str],
                           start_year: Optional[int] = None,
                           end_year: Optional[int] = None) -> Dict:
        """
        Get time series data for one or more BLS series

        Args:
            series_ids: List of BLS series IDs (e.g., ['OEUS000000000000015125200'])
            start_year: Starting year (default: current year - 10)
            end_year: Ending year (default: current year)
        """
        try:
            current_year = datetime.now().year
            start_year = start_year or (current_year - 10)
            end_year = end_year or current_year

            url = f"{self.BASE_URL}/timeseries/data/"

            payload = {
                'seriesid': series_ids,
                'startyear': str(start_year),
                'endyear': str(end_year)
            }

            if self.api_key:
                payload['registrationkey'] = self.api_key

            response = self.session.post(url, json=payload)
            response.raise_for_status()

            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching BLS time series: {e}")
            return {}

    def get_occupation_wages(self, occupation_code: str) -> Optional[WageData]:
        """
        Get wage data for a specific occupation

        Args:
            occupation_code: BLS occupation code (e.g., '15-1252' for Software Developers)
        """
        try:
            # Construct series ID for national wage data
            # Format: OEUN000000000000{occupation_code}03
            # 03 = median hourly wage
            series_id = f"OEUN000000000000{occupation_code.replace('-', '')}03"

            data = self.get_timeseries_data([series_id])

            if data.get('status') == 'REQUEST_SUCCEEDED':
                series_data = data['Results']['series'][0]['data']
                if series_data:
                    latest = series_data[0]  # Most recent data point

                    return WageData(
                        occupation_code=occupation_code,
                        occupation_title=self._get_occupation_title(occupation_code),
                        median_wage=float(latest['value']),
                        mean_wage=float(latest['value']),  # Simplified
                    )

            return None
        except Exception as e:
            logger.error(f"Error fetching wages for {occupation_code}: {e}")
            return None

    def get_employment_trends(self, occupation_code: str,
                            years: int = 5) -> List[EmploymentTrend]:
        """
        Get employment trends for an occupation

        Args:
            occupation_code: BLS occupation code
            years: Number of years of historical data
        """
        try:
            # Construct series ID for employment
            # Format: OEUS000000000000{occupation_code}01
            # 01 = employment level
            series_id = f"OEUS000000000000{occupation_code.replace('-', '')}01"

            current_year = datetime.now().year
            data = self.get_timeseries_data(
                [series_id],
                start_year=current_year - years,
                end_year=current_year
            )

            trends = []
            if data.get('status') == 'REQUEST_SUCCEEDED':
                series_data = data['Results']['series'][0]['data']

                for i, point in enumerate(series_data):
                    year = int(point['year'])
                    employment = int(float(point['value']) * 1000)  # Convert to actual numbers

                    # Calculate year-over-year change
                    change_percent = None
                    if i < len(series_data) - 1:
                        prev_employment = int(float(series_data[i + 1]['value']) * 1000)
                        if prev_employment > 0:
                            change_percent = ((employment - prev_employment) / prev_employment) * 100

                    trends.append(EmploymentTrend(
                        occupation_code=occupation_code,
                        year=year,
                        employment=employment,
                        change_percent=change_percent
                    ))

            return trends
        except Exception as e:
            logger.error(f"Error fetching employment trends for {occupation_code}: {e}")
            return []

    def get_unemployment_rate(self) -> Optional[float]:
        """Get current national unemployment rate"""
        try:
            # Series ID for national unemployment rate
            series_id = "LNS14000000"

            data = self.get_timeseries_data([series_id])

            if data.get('status') == 'REQUEST_SUCCEEDED':
                latest = data['Results']['series'][0]['data'][0]
                return float(latest['value'])

            return None
        except Exception as e:
            logger.error(f"Error fetching unemployment rate: {e}")
            return None

    def _get_occupation_title(self, occupation_code: str) -> str:
        """Get occupation title from code (simplified - would need lookup table)"""
        # This is a simplified version - in production, maintain a lookup table
        occupation_titles = {
            '15-1252': 'Software Developers',
            '15-1256': 'Software Developers and Software Quality Assurance Analysts and Testers',
            '11-2021': 'Marketing Managers',
            '13-2051': 'Financial Analysts'
        }
        return occupation_titles.get(occupation_code, 'Unknown Occupation')


# Example usage
if __name__ == "__main__":
    # You'll need to register for an API key at https://data.bls.gov/registrationEngine/
    service = BLSService(api_key=None)  # Replace with your API key

    # Get wage data for Software Developers
    print("Fetching wage data for Software Developers (15-1252)...")
    wages = service.get_occupation_wages('15-1252')

    if wages:
        print(f"\nOccupation: {wages.occupation_title}")
        print(f"Median Hourly Wage: ${wages.median_wage}")
        print(f"Annual Salary (estimated): ${wages.median_wage * 2080:,.0f}")

    # Get employment trends
    print("\n\nFetching employment trends...")
    trends = service.get_employment_trends('15-1252', years=5)

    if trends:
        print(f"\nEmployment Trends for {trends[0].occupation_code}:")
        for trend in trends:
            change_str = f" ({trend.change_percent:+.1f}%)" if trend.change_percent else ""
            print(f"  {trend.year}: {trend.employment:,} employees{change_str}")

    # Get unemployment rate
    print("\n\nFetching national unemployment rate...")
    unemployment = service.get_unemployment_rate()
    if unemployment:
        print(f"Current Unemployment Rate: {unemployment}%")
