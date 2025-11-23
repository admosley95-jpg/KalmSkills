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

BASE_URL = "https://services.onetcenter.org/ws/online"

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
        """Search for occupations by keyword"""
        try:
            url = f"{BASE_URL}/search"
            params = {'keyword': keyword, 'end': 25}
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get('occupation', [])
        except requests.RequestException as e:
            logger.error(f"Error searching occupations: {e}")
            return []
    
    def get_occupation_details(self, onet_code: str) -> Optional[Occupation]:
        """Get detailed information about a specific occupation"""
        try:
            # Get summary
            url = f"{BASE_URL}/occupations/{onet_code}"
            response = self.session.get(url)
            response.raise_for_status()
            summary = response.json()
            
            # Get skills
            skills = self.get_occupation_skills(onet_code)
            
            return Occupation(
                code=onet_code,
                title=summary.get('title', ''),
                description=summary.get('description', ''),
                skills=skills,
                education_level=self._extract_education(summary)
            )
        except requests.RequestException as e:
            logger.error(f"Error fetching occupation {onet_code}: {e}")
            return None
    
    def get_occupation_skills(self, onet_code: str) -> List[Skill]:
        """Get skills required for an occupation"""
        try:
            url = f"{BASE_URL}/occupations/{onet_code}/summary/skills"
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            
            skills = []
            for skill_data in data.get('skill', []):
                skills.append(Skill(
                    id=skill_data.get('element_id', ''),
                    name=skill_data.get('element_name', ''),
                    description=skill_data.get('description', ''),
                    category='Skill',
                    level=float(skill_data.get('scale_level', {}).get('value', 0)),
                    importance=float(skill_data.get('scale_importance', {}).get('value', 0))
                ))
            
            return skills
        except requests.RequestException as e:
            logger.error(f"Error fetching skills for {onet_code}: {e}")
            return []
    
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
