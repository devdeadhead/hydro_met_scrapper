import os
import requests
from datetime import datetime
from supabase import create_client

# Initialize Supabase Client using repository environment variables
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def scrape_and_store():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }
    
    # Official background streaming data matrix URL
    target_url = "https://hydrology.gov.np/gss/api/socket/nve_snow/response"
    print("Connecting to live streaming node...")
    
    try:
        response = requests.get(target_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            raw_payload = response.json()
            # The portal wraps its entries inside a 'stations' or 'data' array
            stations = raw_payload.get('stations', raw_payload.get('data', []))
            
            river_records = []
            print(f"Connection success. Parsing {len(stations)} potential points...")
            
            for item in stations:
                # Safe fallback extraction checking multiple common government keys
                water_lvl = item.get('water_level', item.get('level', item.get('current_level')))
                
                record = {
                    "station_id": str(item.get('station_id', item.get('id'))),
                    "station_name": item.get('station_name', item.get('name')),
                    "river_name": item.get('river_name', item.get('river')),
                    "water_level": float(water_lvl) if water_lvl is not None else None,
                    "danger_level": float(item.get('danger_level', 0)) if item.get('danger_level') else None,
                    "warning_level": float(item.get('warning_level', 0)) if item.get('warning_level') else None,
                    "recorded_at": item.get('datetime', item.get('timestamp', datetime.utcnow().isoformat()))
                }
                river_records.append(record)
                
            if river_records:
                supabase.table("river_levels").insert(river_records).execute()
                print(f"Success: Synced {len(river_records)} telemetry vectors to your cloud storage!")
            else:
                print("Could not isolate structural elements inside JSON structure.")
                print("Keys available:", list(raw_payload.keys()))
        else:
            print(f"Server response warning. HTTP Status: {response.status_code}")
            
    except Exception as e:
        print(f"Processing exception occurred: {e}")

if __name__ == "__main__":
    scrape_and_store()
