"""
KalmSkills Backend - O*NET Integration Service (Local Database Version)
Parses and searches locally downloaded O*NET database files
"""

import os
import csv
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
        self._load_data()

    def _load_data(self):
        """Load data from text files"""
        if not ONET_DATA_DIR.exists():
            logger.warning(f"O*NET data directory not found at {ONET_DATA_DIR}. Using mock data.")
            return

        logger.info("Loading O*NET database...")

        # Load Occupations
        try:
            with open(ONET_DATA_DIR / "Occupation Data.txt", "r", encoding="utf-8") as f:
                reader = csv.DictReader(f, delimiter="\t")
                for row in reader:
                    self.occupations[row["O*NET-SOC Code"]] = {
                        "title": row["Title"],
                        "description": row["Description"]
                    }
            logger.info(f"Loaded {len(self.occupations)} occupations.")
        except Exception as e:
            logger.error(f"Error loading occupations: {e}")

        # Load Skills
        try:
            # First, get Element Names (Skill names)
            element_names = {} # Element ID -> Name
            with open(ONET_DATA_DIR / "Content Model Reference.txt", "r", encoding="utf-8") as f:
                reader = csv.DictReader(f, delimiter="\t")
                for row in reader:
                    element_names[row["Element ID"]] = {
                        "name": row["Element Name"],
                        "description": row["Description"]
                    }

            # Now load Skills.txt
            # It maps O*NET-SOC Code -> Element ID -> Data Value (Importance/Level)
            # Scale ID: IM (Importance 1-5), LV (Level 0-7)

            temp_skills = {} # code -> element_id -> {importance, level}

            with open(ONET_DATA_DIR / "Skills.txt", "r", encoding="utf-8") as f:
                reader = csv.DictReader(f, delimiter="\t")
                for row in reader:
                    code = row["O*NET-SOC Code"]
                    elem_id = row["Element ID"]
                    scale = row["Scale ID"]
                    value = float(row["Data Value"])

                    if code not in temp_skills:
                        temp_skills[code] = {}
                    if elem_id not in temp_skills[code]:
                        temp_skills[code][elem_id] = {"importance": 0, "level": 0}

                    if scale == "IM":
                        temp_skills[code][elem_id]["importance"] = value
                    elif scale == "LV":
                        temp_skills[code][elem_id]["level"] = value

            # Convert to Skill objects
            for code, elems in temp_skills.items():
                self.skills_data[code] = []
                for elem_id, vals in elems.items():
                    # Only include skills with sufficient importance
                    if vals["importance"] >= 2.0: # Filter low importance
                        skill_info = element_names.get(elem_id, {"name": "Unknown", "description": ""})
                        self.skills_data[code].append(Skill(
                            id=elem_id,
                            name=skill_info["name"],
                            description=skill_info["description"],
                            category="Skill", # Could derive from element ID hierarchy
                            level=vals["level"],
                            importance=vals["importance"]
                        ))

                # Sort by importance
                self.skills_data[code].sort(key=lambda x: x.importance, reverse=True)

            logger.info(f"Loaded skills for {len(self.skills_data)} occupations.")

        except Exception as e:
            logger.error(f"Error loading skills: {e}")

    def search_occupations(self, keyword: str) -> List[Dict]:
        """Search for occupations by keyword in title or description"""
        results = []
        keyword_lower = keyword.lower()

        for code, data in self.occupations.items():
            if keyword_lower in data["title"].lower() or keyword_lower in data["description"].lower():
                results.append({
                    "code": code,
                    "title": data["title"],
                    "description": data["description"]
                })

        # Simple scoring: title match > description match
        results.sort(key=lambda x: 0 if keyword_lower in x["title"].lower() else 1)

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
