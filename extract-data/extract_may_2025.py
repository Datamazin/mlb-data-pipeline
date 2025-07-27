#!/usr/bin/env python3
"""
Extract May 2025 MLB Data
This script will extract detailed game and boxscore data for May 2025.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from src.etl.extract import extract_season_data

def extract_may_2025():
    """Extract detailed MLB data for May 2025."""
    
    print("🏟️  MLB DATA EXTRACTION - MAY 2025")
    print("=" * 60)
    
    print("🗓️  Extracting detailed game and boxscore data for May 2025")
    print("📅 This will include player statistics, boxscores, and game details")
    print("=" * 60)
    
    try:
        # Extract May 2025 data using date range
        print("🔄 Starting May 2025 extraction...")
        
        # May 2025 date range
        start_date = "2025-05-01"
        end_date = "2025-05-31"
        
        stats = extract_season_data(
            year=2025,
            start_date=start_date,
            end_date=end_date,
            save_json=True,
            delay_seconds=1
        )
        
        if stats and stats.get('games_extracted', 0) > 0:
            print(f"\n🎉 Successfully extracted May 2025 data!")
            print(f"✅ Games found: {stats.get('total_games_found', 0)}")
            print(f"✅ Games extracted: {stats.get('games_extracted', 0)}")
            print(f"✅ JSON files saved: {stats.get('json_files_saved', 0)}")
            print(f"✅ Data saved to data/json/2025/05-May/")
            print(f"✅ Ready to load into database with boxscore details")
            
            # Check what was extracted
            may_data_path = Path("data/json/2025/05-May")
            if may_data_path.exists():
                combined_files = list(may_data_path.glob("combined_data_*.json"))
                print(f"📊 Extracted {len(combined_files)} combined data files")
            
            return True
        else:
            print(f"\n❌ Failed to extract May 2025 data or no games found")
            return False
            
    except Exception as e:
        print(f"❌ Error extracting May 2025 data: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = extract_may_2025()
    
    if success:
        print(f"\n🎯 May 2025 extraction completed successfully!")
        print(f"✅ Next step: Run load_may_data.py to load into database")
    else:
        print(f"\n❌ Failed to extract May 2025 data")
        sys.exit(1)
