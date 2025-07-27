#!/usr/bin/env python3
"""
Analyze Game Type Data
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database.connection import DatabaseConnection

def analyze_game_type_data():
    """Analyze the game_type column data in the games table."""
    
    db = DatabaseConnection()
    
    try:
        db.connect()
        
        print("🎮 GAME TYPE ANALYSIS")
        print("=" * 40)
        
        # Check distinct game_type values
        result = db.fetch_results("""
        SELECT game_type, COUNT(*) as count
        FROM games 
        GROUP BY game_type 
        ORDER BY COUNT(*) DESC
        """)
        
        print("Game Type Distribution:")
        total_games = sum(row[1] for row in result)
        for row in result:
            game_type, count = row
            percentage = (count / total_games) * 100 if total_games > 0 else 0
            print(f"  {game_type or 'NULL'}: {count} games ({percentage:.1f}%)")
        
        print(f"\nTotal games: {total_games}")
        
        # Check sample games with their game_type
        sample = db.fetch_results("""
        SELECT TOP 10 game_id, game_date, game_status, game_type 
        FROM games 
        ORDER BY game_date DESC
        """)
        
        print(f"\nSample Games:")
        print("Game ID    Date         Status      Type")
        print("-" * 50)
        for row in sample:
            game_id, date, status, gtype = row
            print(f"{game_id:<10} {date} {status or 'NULL':<10} {gtype or 'NULL'}")
        
        # Check if game_type is being extracted from JSON
        print(f"\nChecking JSON data extraction...")
        
        # Look at a sample JSON file to see if game_type is available
        import json
        import glob
        
        json_files = glob.glob("data/json/2025/04-April/combined_data_*.json")
        if json_files:
            with open(json_files[0], 'r') as f:
                sample_data = json.load(f)
            
            game_data = sample_data.get('game_data', {})
            if 'gameType' in game_data:
                print(f"✅ gameType found in JSON: {game_data['gameType']}")
            elif 'game_type' in game_data:
                print(f"✅ game_type found in JSON: {game_data['game_type']}")
            else:
                print(f"❌ gameType/game_type not found in JSON")
                print(f"Available game_data keys: {list(game_data.keys())}")
        else:
            print("❌ No JSON files found to check")
    
    except Exception as e:
        print(f"❌ Error analyzing game type data: {e}")
    
    finally:
        db.disconnect()

if __name__ == "__main__":
    analyze_game_type_data()
