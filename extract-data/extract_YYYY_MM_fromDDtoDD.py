#!/usr/bin/env python3
"""
Extract MLB Data - Dynamic Date Range
This script will extract detailed game and boxscore data for any custom date range.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.etl.extract import extract_season_data

def extract_mlb_data():
    """Extract detailed MLB data for a custom date range."""
    
    print("🏟️  MLB DATA EXTRACTION - DYNAMIC DATE RANGE")
    print("=" * 60)
    
    # Get user input for date range
    try:
        year = int(input("Enter the year (e.g., 2025): "))
        month = int(input("Enter the month (1-12): "))
        begin_day = int(input("Enter the beginning day of the month (1-31): "))
        end_day = int(input("Enter the ending day of the month (1-31): "))
        
        # Validate input
        if year < 2015 or year > 2030:
            print("❌ Invalid year. Please enter a year between 2015 and 2030.")
            return False
            
        if month < 1 or month > 12:
            print("❌ Invalid month. Please enter a month between 1 and 12.")
            return False
            
        if begin_day < 1 or begin_day > 31 or end_day < 1 or end_day > 31:
            print("❌ Invalid day range. Days must be between 1 and 31.")
            return False
            
        if begin_day > end_day:
            print("❌ Beginning day cannot be greater than ending day.")
            return False
            
        # Validate date exists (basic check for month-day combinations)
        from datetime import datetime
        try:
            datetime(year, month, begin_day)
            datetime(year, month, end_day)
        except ValueError as ve:
            print(f"❌ Invalid date: {ve}")
            return False
            
        # Format dates
        start_date = f"{year}-{month:02d}-{begin_day:02d}"
        end_date = f"{year}-{month:02d}-{end_day:02d}"
        
        # Get month name for display
        month_names = ["", "January", "February", "March", "April", "May", "June",
                      "July", "August", "September", "October", "November", "December"]
        month_name = month_names[month]
        
        print(f"🗓️  Extracting detailed game and boxscore data for {month_name} {begin_day:02d}-{end_day:02d}, {year}")
        print("📅 This will include player statistics, boxscores, and game details")
        print("=" * 60)
        
        # Extract MLB data using date range (custom range)
        print(f"🚀 Starting {month_name} {begin_day:02d}-{end_day:02d}, {year} extraction...")
        
        # Custom date range - year, month, and days specified by user
        # start_date and end_date are already set above
        
        stats = extract_season_data(
            year=year,
            start_date=start_date,
            end_date=end_date,
            save_json=True,
            delay_seconds=1
        )
        
        if stats and stats.get('games_extracted', 0) > 0:
            print(f"\n🎉 Successfully extracted {month_name} {begin_day:02d}-{end_day:02d}, {year} data!")
            print(f"✅ Games found: {stats.get('total_games_found', 0)}")
            print(f"✅ Games extracted: {stats.get('games_extracted', 0)}")
            print(f"✅ JSON files saved: {stats.get('json_files_saved', 0)}")
            print(f"✅ Data saved to data/json/{year}/{month:02d}-{month_name}/")
            print(f"✅ Ready to load into database with boxscore details")
            
            return True
        else:
            print("❌ No data was extracted")
            return False
            
    except ValueError:
        print("❌ Invalid input. Please enter numeric values for days.")
        return False
    except Exception as e:
        print(f"❌ Error during extraction: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = extract_mlb_data()
    if success:
        print(f"\n✅ MLB data extraction completed successfully!")
        print(f"💡 Next step: Load the data into the database using the appropriate loading script")
    else:
        print(f"\n❌ MLB data extraction failed!")
