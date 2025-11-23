"""
KalmSkills Backend - O*NET Integration Service (Local Database Version)
Parses and searches locally downloaded O*NET database files
"""

import os
import csv
import json
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Path to O*NET data
ONET_DATA_DIR = Path("backend/data/onet/extracted/db_29_0_text")

@dataclass
class Skill:
    id: str
    name: str
    description: str
    category: str
    level: float
    importance: float

@dataclass
class Occupation:
    code: str
    title: str
    description: str
    skills: List[Skill]
    education_level: str
    median_salary: Optional[float] = None

class OnetService:
    """Service for querying local O*NET database"""
    
    def __init__(self):
        self.occupations = {}  # code -> {title, description}
        self.skills_data = {}  # code -> List[Skill]
        self.load_error = None
        self.data_path = None
        self._load_data()
    
    def _load_data(self):
        """Load data from JSON cache or text files"""
        # Use absolute path relative to this file to ensure it works on Render
        base_dir = Path(__file__).resolve().parent.parent # backend/
        cache_dir = base_dir / "data" / "onet" / "cache"
        self.data_path = str(cache_dir)
        
        logger.info(f"Current working directory: {os.getcwd()}")
        logger.info(f"Looking for O*NET cache at: {cache_dir}")
        
        # Try loading from JSON cache first (Preferred for Render)
        if (cache_dir / "occupations.json").exists() and (cache_dir / "skills.json").exists():
            logger.info("Loading O*NET data from JSON cache...")
            try:
                # Load Occupations
                with open(cache_dir / "occupations.json", "r", encoding="utf-8") as f:
                    occ_list = json.load(f)
                    for row in occ_list:
                        self.occupations[row["O*NET-SOC Code"]] = {
                            "title": row["Title"],
                            "description": row["Description"]
                        }
                
                # Load Skills
                with open(cache_dir / "skills.json", "r", encoding="utf-8") as f:
                    skills_list = json.load(f)
                    
                    temp_skills = {}
                    for row in skills_list:
                        code = row["O*NET-SOC Code"]
                        elem_id = row["Element ID"]
                        scale = row["Scale ID"]
                        value = float(row["Data Value"])
                        name = row["Element Name"]
                        
                        if code not in temp_skills:
                            temp_skills[code] = {}
                        if elem_id not in temp_skills[code]:
                            temp_skills[code][elem_id] = {
                                "name": name, 
                                "importance": 0, 
                                "level": 0
                            }
                        
                        if scale == "IM":
                            temp_skills[code][elem_id]["importance"] = value
                        elif scale == "LV":
                            temp_skills[code][elem_id]["level"] = value

                    # Convert to Skill objects
                    for code, elems in temp_skills.items():
                        self.skills_data[code] = []
                        for elem_id, vals in elems.items():
                            if vals["importance"] >= 2.0:
                                self.skills_data[code].append(Skill(
                                    id=elem_id,
                                    name=vals["name"],
                                    description="", 
                                    category="Skill",
                                    level=vals["level"],
                                    importance=vals["importance"]
                                ))
                        self.skills_data[code].sort(key=lambda x: x.importance, reverse=True)

                logger.info(f"Loaded {len(self.occupations)} occupations from cache.")
                return

            except Exception as e:
                self.load_error = str(e)
                logger.error(f"Error loading from cache: {e}")
        else:
            self.load_error = f"Cache files not found at {cache_dir}"
            logger.warning(self.load_error)

        # Fallback to text files
        if not ONET_DATA_DIR.exists():
            logger.warning(f"O*NET data directory not found at {ONET_DATA_DIR}. Using mock data.")
            return


    def search_occupations(self, keyword: str) -> List[Dict]:
        """Search for occupations by keyword in title or description"""
        results = []
        query_lower = keyword.lower()
        keywords = query_lower.split()
        
        if not keywords:
            return []
        
        for code, data in self.occupations.items():
            text = (data["title"] + " " + data["description"]).lower()
            score = 0
            
            # Exact phrase match bonus
            if query_lower in text:
                score += 50
            
            # Keyword match
            matches = 0
            for word in keywords:
                if len(word) > 2 and word in text: # Ignore short words
                    matches += 1
            
            if matches > 0:
                score += matches * 10
            
            if score > 0:
                results.append({
                    "code": code,
                    "title": data["title"],
                    "description": data["description"],
                    "score": score
                })
        
        # Sort by score
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return results

    def get_occupation_details(self, onet_code: str) -> Optional[Occupation]:
        """Get detailed information about a specific occupation"""
        if onet_code not in self.occupations:
            return None
        
        data = self.occupations[onet_code]
        skills = self.get_occupation_skills(onet_code)
        
        return Occupation(
            code=onet_code,
            title=data["title"],
            description=data["description"],
            skills=skills,
            education_level="Bachelor's degree" # Placeholder, Education.txt would need parsing
        )
    
    def get_occupation_skills(self, onet_code: str) -> List[Skill]:
        """Get skills required for an occupation"""
        return self.skills_data.get(onet_code, [])

    def get_technology_skills(self, onet_code: str) -> List[str]:
        """Get technology skills (from Technology Skills.txt if implemented)"""
        # Placeholder for MVP
        return []

# Test run
if __name__ == "__main__":
    svc = OnetService()
    print(svc.search_occupations("software")[:2])
