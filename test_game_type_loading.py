#!/usr/bin/env python3
"""
Test Game Type Extraction and Loading
"""

import os
import sys
import json
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database.connection import DatabaseConnection
from database.json_to_sql_loader import JSONToSQLLoader

def test_game_type_loading():
    """Test if game type can be extracted and loaded properly."""
    
    print("🧪 TESTING GAME TYPE EXTRACTION AND LOADING")
    print("=" * 60)
    
    # First, let's create a sample combined data file with game type
    sample_combined_data = {
        "game_id": 999999,  # Test game ID
        "game_date": "2025-04-15",
        "extraction_timestamp": "2025-07-27T12:00:00",
        "home_team": "Test Home Team",
        "away_team": "Test Away Team", 
        "game_status": "Final",
        "game_type": "R",  # Regular season
        "official_date": "2025-04-15",
        "series_description": "Regular Season",
        "boxscore": {
            "teams": {
                "home": {
                    "team": {"id": 999, "name": "Test Home Team"},
                    "players": {}
                },
                "away": {
                    "team": {"id": 998, "name": "Test Away Team"},
                    "players": {}
                }
            }
        },
        "game_data": {
            "teams": {
                "home": {"team": {"id": 999}, "runs": 5},
                "away": {"team": {"id": 998}, "runs": 3}
            },
            "currentInning": 9,
            "inningState": "End"
        }
    }
    
    # Save test file
    test_file = "test_combined_data_999999.json"
    with open(test_file, 'w') as f:
        json.dump(sample_combined_data, f, indent=2)
    
    print(f"1. Created test file: {test_file}")
    
    # Test loading
    loader = JSONToSQLLoader()
    
    try:
        print("2. Testing JSON loading...")
        success = loader.load_json_to_database(test_file)
        
        if success:
            print("   ✅ Test data loaded successfully")
            
            # Check if game type was stored correctly
            print("3. Checking database for game type...")
            db = DatabaseConnection()
            db.connect()
            
            result = db.fetch_results("""
            SELECT game_id, game_type, series_description, official_date, game_date
            FROM games 
            WHERE game_id = 999999
            """)
            
            if result:
                game_id, game_type, series_desc, official_date, game_date = result[0]
                print(f"   ✅ Game found in database:")
                print(f"     Game ID: {game_id}")
                print(f"     Game Type: {game_type}")
                print(f"     Series Description: {series_desc}")
                print(f"     Official Date: {official_date}")
                print(f"     Game Date: {game_date}")
                
                if game_type == "R":
                    print("   🎉 Game type was stored correctly!")
                else:
                    print(f"   ❌ Game type mismatch. Expected 'R', got '{game_type}'")
            else:
                print("   ❌ Test game not found in database")
            
            # Clean up test data
            print("4. Cleaning up test data...")
            db.execute_query("DELETE FROM boxscore WHERE game_id = 999999")
            db.execute_query("DELETE FROM games WHERE game_id = 999999")
            db.execute_query("DELETE FROM teams WHERE team_id IN (998, 999)")
            print("   ✅ Test data cleaned up")
            
            db.disconnect()
        else:
            print("   ❌ Failed to load test data")
    
    except Exception as e:
        print(f"❌ Error during testing: {e}")
    
    finally:
        # Clean up test file
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"   🗑️  Removed test file: {test_file}")

if __name__ == "__main__":
    test_game_type_loading()
