#!/usr/bin/env python3
"""
Extract June 2025 MLB Data
This script will extract detailed game and boxscore data for June 2025.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from src.etl.extract import extract_season_data

def extract_june_2025():
    """Extract detailed MLB data for June 2025."""
    
    print("🏟️  MLB DATA EXTRACTION - JUNE 2025")
    print("=" * 60)
    
    print("🗓️  Extracting detailed game and boxscore data for June 2025")
    print("📅 This will include player statistics, boxscores, and game details")
    print("=" * 60)
    
    try:
        # Extract June 2025 data using date range
        print("� Starting June 2025 extraction...")
        
        # June 2025 date range
        start_date = "2025-06-01"
        end_date = "2025-06-30"
        
        stats = extract_season_data(
            year=2025,
            start_date=start_date,
            end_date=end_date,
            save_json=True,
            delay_seconds=1
        )
        
        if stats and stats.get('games_extracted', 0) > 0:
            print(f"\n🎉 Successfully extracted June 2025 data!")
            print(f"✅ Games found: {stats.get('total_games_found', 0)}")
            print(f"✅ Games extracted: {stats.get('games_extracted', 0)}")
            print(f"✅ JSON files saved: {stats.get('json_files_saved', 0)}")
            print(f"✅ Data saved to data/json/2025/06-June/")
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
    success = extract_june_2025()
    if success:
        print(f"\n✅ June 2025 extraction completed successfully!")
        print(f"💡 Next step: Run 'python load_june_data.py' to load the data into the database")
    else:
        print(f"\n❌ June 2025 extraction failed!")

if __name__ == "__main__":
    success = extract_june_2025()
    if success:
        print(f"\n✅ June 2025 extraction completed successfully!")
        print(f"💡 Next step: Run 'python load_june_data.py' to load the data into the database")
    else:
        print(f"\n❌ June 2025 extraction failed!")
