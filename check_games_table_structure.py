#!/usr/bin/env python3
"""
Check Games Table Structure
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database.connection import DatabaseConnection

def check_games_table_structure():
    """Check the current structure of the dbo.games table."""
    
    db = DatabaseConnection()
    
    try:
        db.connect()
        
        print("📊 CHECKING GAMES TABLE STRUCTURE")
        print("=" * 50)
        
        # Get table structure
        result = db.fetch_results("""
        SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = 'games'
        ORDER BY ORDINAL_POSITION
        """)
        
        print("Column Name".ljust(20) + "Data Type".ljust(15) + "Nullable".ljust(10) + "Default")
        print("-" * 60)
        for row in result:
            col_name, data_type, nullable, default = row
            print(f"{col_name}".ljust(20) + f"{data_type}".ljust(15) + f"{nullable}".ljust(10) + f"{default or ''}".ljust(15))
        
        print(f"\nTotal columns: {len(result)}")
        
        # Check if game_type column exists
        game_type_exists = any(row[0] == 'game_type' for row in result)
        print(f"game_type column exists: {game_type_exists}")
        
        # Check what columns are missing from the schema definition
        expected_columns = [
            'game_id', 'game_date', 'home_team_id', 'away_team_id', 
            'home_score', 'away_score', 'inning', 'inning_state', 
            'game_status', 'game_type', 'series_description', 'official_date', 'created_at'
        ]
        
        actual_columns = [row[0] for row in result]
        missing_columns = [col for col in expected_columns if col not in actual_columns]
        extra_columns = [col for col in actual_columns if col not in expected_columns]
        
        if missing_columns:
            print(f"\n❌ Missing columns: {missing_columns}")
        else:
            print(f"\n✅ All expected columns present")
            
        if extra_columns:
            print(f"➕ Extra columns: {extra_columns}")
        
        # Sample game data to see what's actually stored
        print(f"\n📋 SAMPLE GAME DATA:")
        sample_games = db.fetch_results("""
        SELECT TOP 5 game_id, game_date, game_status
        FROM games
        ORDER BY game_date DESC
        """)
        
        if sample_games:
            print("Game ID    Date         Status")
            print("-" * 35)
            for row in sample_games:
                game_id, game_date, status = row
                print(f"{game_id:<10} {game_date} {status or 'NULL'}")
        else:
            print("No games found in database")
    
    except Exception as e:
        print(f"❌ Error checking table structure: {e}")
    
    finally:
        db.disconnect()

if __name__ == "__main__":
    check_games_table_structure()
