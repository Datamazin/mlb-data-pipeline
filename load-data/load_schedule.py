#!/usr/bin/env python3
"""
Script to load MLB schedule data into the games table.
This will populate the games table with proper schedule information.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from src.api.mlb_client import MLBClient
from src.database.json_to_sql_loader import JSONToSQLLoader

def load_schedule_for_month(year, month):
    """Load MLB schedule for a specific month."""
    
    # Calculate start and end dates for the month
    start_date = datetime(year, month, 1)
    
    # Get last day of month
    if month == 12:
        end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = datetime(year, month + 1, 1) - timedelta(days=1)
    
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    
    print(f"🗓️  Loading MLB schedule for {start_date.strftime('%B %Y')}")
    print(f"📅 Date range: {start_date_str} to {end_date_str}")
    print("=" * 60)
    
    try:
        # Initialize MLB client and loader
        mlb_client = MLBClient()
        loader = JSONToSQLLoader()
        
        # Fetch schedule data
        print("🔄 Fetching schedule from MLB API...")
        schedule_data = mlb_client.fetch_schedule(start_date_str, end_date_str)
        
        # Count total games
        total_games = sum(len(date_entry.get('games', [])) for date_entry in schedule_data.get('dates', []))
        print(f"📊 Found {total_games} games in schedule")
        
        if total_games == 0:
            print("⚠️  No games found in the specified date range")
            return False
        
        # Load schedule data into database
        print("💾 Loading schedule data into database...")
        success = loader.load_schedule_data(schedule_data)
        
        if success:
            print(f"\n🎉 Successfully loaded {start_date.strftime('%B %Y')} schedule!")
            print(f"✅ {total_games} games added to the database")
        else:
            print(f"\n❌ Failed to load schedule data")
            
        return success
        
    except Exception as e:
        print(f"❌ Error loading schedule: {e}")
        return False

def load_schedule_for_date_range(start_date, end_date):
    """Load MLB schedule for a date range."""
    
    print(f"🗓️  Loading MLB schedule from {start_date} to {end_date}")
    print("=" * 60)
    
    try:
        # Initialize MLB client and loader
        mlb_client = MLBClient()
        loader = JSONToSQLLoader()
        
        # Fetch schedule data
        print("🔄 Fetching schedule from MLB API...")
        schedule_data = mlb_client.fetch_schedule(start_date, end_date)
        
        # Count total games
        total_games = sum(len(date_entry.get('games', [])) for date_entry in schedule_data.get('dates', []))
        print(f"📊 Found {total_games} games in schedule")
        
        if total_games == 0:
            print("⚠️  No games found in the specified date range")
            return False
        
        # Load schedule data into database
        print("💾 Loading schedule data into database...")
        success = loader.load_schedule_data(schedule_data)
        
        if success:
            print(f"\n🎉 Successfully loaded schedule!")
            print(f"✅ {total_games} games added to the database")
        else:
            print(f"\n❌ Failed to load schedule data")
            
        return success
        
    except Exception as e:
        print(f"❌ Error loading schedule: {e}")
        return False

if __name__ == "__main__":
    # Load March and April 2025 schedule with game type information
    print("🏟️  MLB Schedule Loader - March & April 2025")
    print("=" * 60)
    
    success_count = 0
    total_months = 2
    
    # Load March 2025
    print("\n📅 Loading March 2025...")
    if load_schedule_for_month(2025, 3):
        success_count += 1
        print("✅ March 2025 loaded successfully")
    else:
        print("❌ March 2025 failed to load")
    
    # Load April 2025  
    print("\n📅 Loading April 2025...")
    if load_schedule_for_month(2025, 4):
        success_count += 1
        print("✅ April 2025 loaded successfully")
    else:
        print("❌ April 2025 failed to load")
    
    # Summary
    print(f"\n📊 SUMMARY:")
    print(f"Successfully loaded: {success_count}/{total_months} months")
    
    if success_count == total_months:
        print("\n🎯 All schedule data loaded successfully!")
        print("✅ dbo.games table now includes game_type information for March & April 2025")
    else:
        print(f"\n⚠️  Partial success: {success_count}/{total_months} months loaded")
        sys.exit(1)
