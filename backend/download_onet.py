"""
Script to download O*NET 29.0 Database files directly.
"""
import os
import requests
import zipfile
import io
import shutil
from pathlib import Path

# O*NET 29.0 Database URL (Text format)
ONET_URL = "https://www.onetcenter.org/dl_files/database/db_29_0_text.zip"
OUTPUT_DIR = Path("backend/data/onet")
EXTRACT_DIR = OUTPUT_DIR / "extracted"

def download_onet_data():
    print(f"Downloading O*NET data from {ONET_URL}...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    EXTRACT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        response = requests.get(ONET_URL, stream=True)
        response.raise_for_status()

        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            z.extractall(EXTRACT_DIR)
            print(f"Extracted to {EXTRACT_DIR}")

            # List extracted files
            extracted_files = []
            for root, dirs, files in os.walk(EXTRACT_DIR):
                for file in files:
                    extracted_files.append(os.path.join(root, file))

            print(f"Found {len(extracted_files)} files.")
            return True

    except Exception as e:
        print(f"Error downloading O*NET data: {e}")
        return False

if __name__ == "__main__":
    download_onet_data()
