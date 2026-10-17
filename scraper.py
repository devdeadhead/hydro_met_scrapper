import os
import requests
from datetime import datetime
from supabase import create_client

# Initialize Supabase Client using repository environment variables
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def scrape_and_store():
    # Complete realistic profile signatures to bypass firewalls natively
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://hydrology.gov.np",
        "Origin": "https://hydrology.gov.np",
        "Connection": "keep-alive"
    }
    
    # Clean background direct database JSON channel link destination path
    river_url = "https://hydrology.gov.npgss/api/river_watch"
    print("Initiating direct data packet sync operation...")
    
    try:
        response = requests.get(river_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            payload = response.json()
            data_list = payload.get('data', payload.get('stations', []))
            river_records = []
            
            for item in data_list:
                water_lvl = item.get('water_level', item.get('level'))
                if item.get('station_name') and water_lvl is not None:
                    record = {
                        "station_id": str(item.get('station_id', item.get('id'))),
                        "station_name": item.get('station_name'),
                        "river_name": item.get('river_name', 'Unknown'),
                        "water_level": float(water_lvl),
                        "danger_level": float(item.get('danger_level')) if item.get('danger_level') else None,
                        "warning_level": float(item.get('warning_level')) if item.get('warning_level') else None,
                        "recorded_at": item.get('datetime', datetime.utcnow().isoformat())
                    }
                    river_records.append(record)
            
            if river_records:
                supabase.table("river_levels").insert(river_records).execute()
                print(f"Success: Synced {len(river_records)} telemetry vectors to your cloud storage!")
            else:
                print("Connected but no matching fields found in the payload schema structure.")
        else:
            print(f"Firewall block encountered. Server responded with status: {response.status_code}")
            
    except Exception as e:
        print(f"An error occurred during database commit operations: {e}")

if __name__ == "__main__":
    scrape_and_store()
