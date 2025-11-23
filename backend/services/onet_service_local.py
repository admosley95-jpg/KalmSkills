"""
KalmSkills Backend - O*NET Integration Service (Local Database)
Uses downloaded O*NET database files instead of API
"""

import json
from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Path to cached O*NET data
CACHE_DIR = Path(__file__).parent.parent / "data" / "onet" / "cache"

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
    """Service for interacting with local O*NET database"""
    
    def __init__(self):
        self.occupations = self._load_occupations()
        self.skills = self._load_skills()
        logger.info(f"Loaded {len(self.occupations)} occupations and {len(self.skills)} skill records")
    
    def _load_occupations(self) -> List[Dict]:
        """Load occupations from cached JSON"""
        cache_file = CACHE_DIR / "occupations.json"
        if not cache_file.exists():
            logger.warning(f"Occupations cache not found at {cache_file}. Run download_onet.py first.")
            return []
        
        with open(cache_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_skills(self) -> List[Dict]:
        """Load skills from cached JSON"""
        cache_file = CACHE_DIR / "skills.json"
        if not cache_file.exists():
            logger.warning(f"Skills cache not found at {cache_file}. Run download_onet.py first.")
            return []
        
        with open(cache_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def search_occupations(self, keyword: str) -> List[Dict]:
        """Search for occupations by keyword in real O*NET data"""
        keyword_lower = keyword.lower()
        results = []
        
        for occ in self.occupations:
            title = str(occ.get('Title', '')).lower()
            desc = str(occ.get('Description', '')).lower()
            code = str(occ.get('O*NET-SOC Code', ''))
            
            if keyword_lower in title or keyword_lower in desc:
                results.append({
                    'code': code,
                    'title': occ.get('Title', ''),
                    'description': desc[:200]  # First 200 chars
                })
            
            if len(results) >= 25:
                break
        
        logger.info(f"Found {len(results)} occupations for '{keyword}'")
        return results
    
    def get_occupation_details(self, onet_code: str) -> Optional[Occupation]:
        """Get detailed information about a specific occupation from real data"""
        # Find occupation
        occ_data = None
        for occ in self.occupations:
            if occ.get('O*NET-SOC Code') == onet_code:
                occ_data = occ
                break
        
        if not occ_data:
            logger.warning(f"Occupation {onet_code} not found")
            return None
        
        # Get skills for this occupation
        skills = self.get_occupation_skills(onet_code)
        
        return Occupation(
            code=onet_code,
            title=occ_data.get('Title', ''),
            description=occ_data.get('Description', '')[:500],  # Truncate long descriptions
            skills=skills,
            education_level="Bachelor's degree"  # Would need Education table for accurate data
        )
    
    def get_occupation_skills(self, onet_code: str) -> List[Skill]:
        """Get skills required for an occupation from real O*NET data"""
        occupation_skills = []
        
        for skill_record in self.skills:
            if skill_record.get('O*NET-SOC Code') == onet_code:
                # Only use 'Importance' scale for skills (skip 'Level' to avoid duplicates)
                if skill_record.get('Scale Name') == 'Importance':
                    occupation_skills.append(Skill(
                        id=skill_record.get('Element ID', ''),
                        name=skill_record.get('Element Name', ''),
                        description=skill_record.get('Description', ''),
                        category=skill_record.get('Scale Name', 'Skill'),
                        level=float(skill_record.get('Data Value', 0)) if skill_record.get('Data Value') else None,
                        importance=float(skill_record.get('Data Value', 0)) if skill_record.get('Data Value') else None
                    ))
        
        # If no skills found, try related occupations (e.g., 15-1252.00 -> 15-1253.00)
        if not occupation_skills and onet_code:
            similar_code = onet_code[:6]  # Get first 6 chars like '15-125'
            logger.warning(f"No skills found for {onet_code}, searching for similar codes: {similar_code}*")
            
            for skill_record in self.skills:
                if skill_record.get('O*NET-SOC Code', '').startswith(similar_code):
                    if skill_record.get('Scale Name') == 'Importance':
                        occupation_skills.append(Skill(
                            id=skill_record.get('Element ID', ''),
                            name=skill_record.get('Element Name', ''),
                            description=skill_record.get('Description', ''),
                            category=skill_record.get('Scale Name', 'Skill'),
                            level=float(skill_record.get('Data Value', 0)) if skill_record.get('Data Value') else None,
                            importance=float(skill_record.get('Data Value', 0)) if skill_record.get('Data Value') else None
                        ))
                    if len(occupation_skills) >= 20:
                        break
        
        logger.info(f"Found {len(occupation_skills)} skills for {onet_code}")
        return occupation_skills[:20]  # Return top 20 skills
    
    def get_technology_skills(self, onet_code: str) -> List[str]:
        """Get technology/tool skills for an occupation"""
        # Technology skills would require loading Technology Skills.xlsx
        # For now, return empty list - can be enhanced later
        return []


# Example usage
if __name__ == "__main__":
    service = OnetService()
    
    # Search for software developer jobs
    print("\nSearching for 'software developer'...")
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
            print(f"\nSkills ({len(occupation.skills)}):")
            for skill in occupation.skills[:5]:
                print(f"  - {skill.name} (Level: {skill.level}, Importance: {skill.importance})")
