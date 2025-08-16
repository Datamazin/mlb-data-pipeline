#!/usr/bin/env python3
"""
Extract August 2025 MLB Data (Up to August 15)
This script will extract detailed game and boxscore data for August 1-15, 2025.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from src.etl.extract import extract_season_data

def extract_august_2025():
    """Extract detailed MLB data for August 1-15, 2025."""
    
    print("🏟️  MLB DATA EXTRACTION - AUGUST 2025 (Aug 1-15)")
    print("=" * 60)
    
    print("🗓️  Extracting detailed game and boxscore data for August 1-15, 2025")
    print("📅 This will include player statistics, boxscores, and game details")
    print("=" * 60)
    
    try:
        # Extract August 1-15, 2025 data using date range
        print("🚀 Starting August 2025 extraction...")
        
        # August 1-15, 2025 date range (up to current date)
        start_date = "2025-08-01"
        end_date = "2025-08-15"  # Current date
        
        print(f"📅 Date range: {start_date} to {end_date}")
        
        stats = extract_season_data(
            year=2025,
            start_date=start_date,
            end_date=end_date,
            save_json=True,
            delay_seconds=1
        )
        
        if stats and stats.get('games_extracted', 0) > 0:
            print(f"\n🎉 Successfully extracted August 2025 data!")
            print(f"✅ Games found: {stats.get('total_games_found', 0)}")
            print(f"✅ Games extracted: {stats.get('games_extracted', 0)}")
            print(f"✅ JSON files saved: {stats.get('json_files_saved', 0)}")
            print(f"✅ Data saved to data/json/2025/08-August/")
            print(f"✅ Ready to load into database with boxscore details")
            
            return True
        else:
            print("❌ No data was extracted")
            return False
            
    except Exception as e:
        print(f"❌ Error during extraction: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = extract_august_2025()
    if success:
        print(f"\n✅ August 2025 extraction completed successfully!")
        print(f"💡 Next step: Run 'python load_dynamic_date_range_data.py --start 2025-08-01 --end 2025-08-15' to load the data")
    else:
        print(f"\n❌ August 2025 extraction failed!")
