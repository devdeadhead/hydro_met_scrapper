import os
import requests
from datetime import datetime
from supabase import create_client

# Initialize Supabase Client using repository environment variables
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def scrape_and_store():
    # Simulated browser headers to prevent tracking blockades and parsing errors
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*"
    }
    
    river_url = "https://hydrology.gov.np"
    print("Initiating connection to DHM River Telemetry API...")
    
    try:
        response = requests.get(river_url, headers=headers, timeout=30)
        
        # Guard clause to ensure the server response is actual data and not HTML
        if response.status_code == 200 and "application/json" in response.headers.get("Content-Type", ""):
            data = response.json().get('data', [])
            river_records = []
            
            for item in data:
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
                
            if river_records:
                supabase.table("river_levels").insert(river_records).execute()
                print(f"Success: Stored {len(river_records)} tracking nodes to river_levels.")
            else:
                print("No data array items detected inside payload.")
        else:
            print(f"Blocked or alternative layout received. HTTP {response.status_code}. Content-Type: {response.headers.get('Content-Type')}")
            print("Returned text sample:", response.text[:200])
            
    except Exception as e:
        print(f"An error occurred during database commit operations: {e}")

if __name__ == "__main__":
    scrape_and_store()
