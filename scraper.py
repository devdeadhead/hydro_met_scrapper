import os
import requests
from datetime import datetime
from supabase import create_client

# Initialize Supabase Client using repository environment variables
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def scrape_and_store():
    # 1. Fetch River Data
    river_url = "https://hydrology.gov.np"
    
    try:
        response = requests.get(river_url, timeout=30)
        if response.status_code == 200:
            data = response.json().get('data', [])
            river_records = []
            
            for item in data:
                # Map keys precisely to avoid adding empty or extra metadata columns
                record = {
                    "station_id": str(item.get('station_id')),
                    "station_name": item.get('station_name'),
                    "river_name": item.get('river_name'),
                    "water_level": float(item.get('water_level')) if item.get('water_level') else None,
                    "danger_level": float(item.get('danger_level')) if item.get('danger_level') else None,
                    "warning_level": float(item.get('warning_level')) if item.get('warning_level') else None,
                    "recorded_at": item.get('datetime')
                }
                river_records.append(record)
                
            # Insert into your Supabase database table
            if river_records:
                supabase.table("river_levels").insert(river_records).execute()
                print(f"Successfully logged {len(river_records)} river stations.")
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    scrape_and_store()
