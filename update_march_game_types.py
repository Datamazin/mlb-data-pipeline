#!/usr/bin/env python3
"""
Update Game Types for March 2025 Data
Fetches schedule data and updates existing games with game type information.
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from api.mlb_client import MLBClient
from database.json_to_sql_loader import JSONToSQLLoader

def update_march_2025_game_types():
    """Update game type information for March 2025 games."""
    client = MLBClient()
    loader = JSONToSQLLoader()
    
    print("🔄 Updating game type information for March 2025...")
    
    try:
        # Fetch schedule for March 2025
        print("📅 Fetching March 2025 schedule from MLB API...")
        schedule_data = client.fetch_schedule('2025-03-01', '2025-03-31')
        
        # Load schedule data to update game types
        print("💾 Updating database with game type information...")
        success = loader.load_schedule_data(schedule_data)
        
        if success:
            print("✅ Game type information updated successfully!")
            
            # Show summary of what was updated
            from game_type_analyzer import GameTypeAnalyzer
            analyzer = GameTypeAnalyzer()
            analyzer.print_game_type_summary()
            
        else:
            print("❌ Failed to update game type information")
            
        return success
        
    except Exception as e:
        print(f"❌ Error updating game types: {e}")
        return False

if __name__ == "__main__":
    success = update_march_2025_game_types()
    if success:
        print("\n✅ March 2025 game types updated!")
    else:
        print("\n❌ Failed to update game types!")
