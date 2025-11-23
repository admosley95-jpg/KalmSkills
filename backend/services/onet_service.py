"""
KalmSkills Backend - O*NET Integration Service
Fetches and processes occupational data from O*NET Online
"""

import requests
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# O*NET requires authentication for API access
# Using public web endpoint instead for MVP
BASE_URL = "https://services.onetcenter.org/ws"
# Note: For production, register at https://services.onetcenter.org/developer/web to get API credentials

@dataclass
class Skill:
    id: str
    name: str
    description: str
    category: str
    level: Optional[float] = None
    importance: Optional[float] = None

@dataclass
class Occupation:
    code: str
    title: str
    description: str
    skills: List[Skill]
    education_level: str
    median_salary: Optional[float] = None

class OnetService:
    """Service for interacting with O*NET Web Services"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'KalmSkills/1.0 (contact@kalmskills.ai)',
            'Accept': 'application/json'
        })
    
    def search_occupations(self, keyword: str) -> List[Dict]:
        """Search for occupations by keyword - returns mock data for MVP"""
        # O*NET API requires authentication - using mock data for demo
        # For production: Register at https://services.onetcenter.org/developer/web
        
        logger.info(f"Searching for occupations: {keyword}")
        
        # Mock occupation data based on common searches
        mock_occupations = {
            'software': [
                {'code': '15-1252.00', 'title': 'Software Developers', 'tags': ['python', 'javascript', 'react', 'programming']},
                {'code': '15-1256.00', 'title': 'Software Quality Assurance Analysts', 'tags': ['testing', 'qa']},
            ],
            'data': [
                {'code': '15-2051.00', 'title': 'Data Scientists', 'tags': ['python', 'machine learning', 'sql', 'analytics']},
                {'code': '15-2041.00', 'title': 'Statisticians', 'tags': ['statistics', 'analysis']},
            ],
            'financial': [
                {'code': '13-2051.00', 'title': 'Financial Analysts', 'tags': ['finance', 'excel', 'modeling']},
                {'code': '11-3031.00', 'title': 'Financial Managers', 'tags': ['leadership', 'finance']},
            ]
        }
        
        keyword_lower = keyword.lower()
        results = []
        
        for category, occupations in mock_occupations.items():
            if category in keyword_lower or any(tag in keyword_lower for occ in occupations for tag in occ['tags']):
                results.extend(occupations)
        
        # Default to software developer if no match
        if not results:
            results = mock_occupations['software']
        
        return results[:10]
    
    def get_occupation_details(self, onet_code: str) -> Optional[Occupation]:
        """Get detailed information about a specific occupation - mock data for MVP"""
        logger.info(f"Fetching occupation details: {onet_code}")
        
        # Mock occupation details
        mock_details = {
            '15-1252.00': {
                'title': 'Software Developers',
                'description': 'Research, design, and develop computer and network software or specialized utility programs.',
                'education': "Bachelor's degree"
            },
            '15-2051.00': {
                'title': 'Data Scientists',
                'description': 'Develop and implement a set of techniques or analytics applications to transform raw data into meaningful information.',
                'education': "Master's degree"
            },
            '13-2051.00': {
                'title': 'Financial Analysts',
                'description': 'Conduct quantitative analyses of information involving investment programs or financial data of public or private institutions.',
                'education': "Bachelor's degree"
            }
        }
        
        details = mock_details.get(onet_code, mock_details['15-1252.00'])
        skills = self.get_occupation_skills(onet_code)
        
        return Occupation(
            code=onet_code,
            title=details['title'],
            description=details['description'],
            skills=skills,
            education_level=details['education']
        )
    
    def get_occupation_skills(self, onet_code: str) -> List[Skill]:
        """Get skills required for an occupation - mock data for MVP"""
        logger.info(f"Fetching skills for: {onet_code}")
        
        # Mock skills based on occupation
        mock_skills = {
            '15-1252.00': [  # Software Developers
                Skill('2.A.1.a', 'Reading Comprehension', 'Understanding written sentences and paragraphs', 'Basic Skills', 3.5, 3.8),
                Skill('2.A.1.b', 'Active Listening', 'Giving full attention to what other people are saying', 'Basic Skills', 3.2, 3.5),
                Skill('2.C.1.a', 'Programming', 'Writing computer programs for various purposes', 'Technical Skills', 4.5, 4.8),
                Skill('2.C.1.b', 'Systems Analysis', 'Determining how a system should work', 'Technical Skills', 4.2, 4.5),
            ],
            '15-2051.00': [  # Data Scientists
                Skill('2.A.1.a', 'Mathematics', 'Using mathematics to solve problems', 'Basic Skills', 4.5, 4.8),
                Skill('2.C.1.a', 'Programming', 'Writing computer programs for various purposes', 'Technical Skills', 4.3, 4.6),
                Skill('2.C.1.c', 'Data Analysis', 'Analyzing data to identify trends', 'Technical Skills', 4.7, 4.9),
            ],
            '13-2051.00': [  # Financial Analysts
                Skill('2.A.1.a', 'Mathematics', 'Using mathematics to solve problems', 'Basic Skills', 4.0, 4.3),
                Skill('2.C.1.d', 'Financial Analysis', 'Analyzing financial data', 'Technical Skills', 4.5, 4.8),
            ]
        }
        
        return mock_skills.get(onet_code, mock_skills['15-1252.00'])
    
    def get_technology_skills(self, onet_code: str) -> List[str]:
        """Get technology/tool skills for an occupation"""
        try:
            url = f"{BASE_URL}/occupations/{onet_code}/summary/technology"
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            
            tech_skills = []
            for category in data.get('technology', []):
                for example in category.get('example', []):
                    tech_skills.append(example.get('name', ''))
            
            return tech_skills
        except requests.RequestException as e:
            logger.error(f"Error fetching technology skills for {onet_code}: {e}")
            return []
    
    def _extract_education(self, summary: Dict) -> str:
        """Extract education level from occupation summary"""
        # This would need to parse education requirements from the summary
        # Simplified for now
        return "Bachelor's degree"


# Example usage
if __name__ == "__main__":
    service = OnetService()
    
    # Search for software developer jobs
    print("Searching for 'software developer'...")
    results = service.search_occupations("software developer")
    
    if results:
        print(f"\nFound {len(results)} occupations")
        first_result = results[0]
        print(f"\nFirst result: {first_result['title']} ({first_result['code']})")
        
        # Get detailed information
        print("\nFetching detailed information...")
        occupation = service.get_occupation_details(first_result['code'])
        
        if occupation:
            print(f"\nOccupation: {occupation.title}")
            print(f"Description: {occupation.description[:200]}...")
            print(f"\nTop Skills:")
            for skill in occupation.skills[:5]:
                print(f"  - {skill.name} (Level: {skill.level}, Importance: {skill.importance})")
            
            # Get technology skills
            tech_skills = service.get_technology_skills(first_result['code'])
            print(f"\nTechnology Skills ({len(tech_skills)}):")
            for tech in tech_skills[:10]:
                print(f"  - {tech}")
