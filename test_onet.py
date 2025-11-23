
import sys
import os
import json
from pathlib import Path

# Add the current directory to sys.path so we can import from backend
sys.path.append(os.getcwd())

from backend.services.onet_service import OnetService

def test_onet_loading():
    print("Testing O*NET Service Loading...")
    
    # Check if files exist
    cache_dir = Path("backend/data/onet/cache")
    occ_path = cache_dir / "occupations.json"
    skills_path = cache_dir / "skills.json"
    
    print(f"Occupations path: {occ_path}, Exists: {occ_path.exists()}")
    if occ_path.exists():
        print(f"Occupations size: {occ_path.stat().st_size} bytes")
        
    print(f"Skills path: {skills_path}, Exists: {skills_path.exists()}")
    if skills_path.exists():
        print(f"Skills size: {skills_path.stat().st_size} bytes")

    try:
        svc = OnetService()
        print(f"Loaded {len(svc.occupations)} occupations")
        print(f"Loaded skills for {len(svc.skills_data)} occupations")
        
        # Test search
        results = svc.search_occupations("construction work")
        print(f"Search 'construction work' returned {len(results)} results")
        if results:
            print("Top result:", results[0]['title'])
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_onet_loading()
