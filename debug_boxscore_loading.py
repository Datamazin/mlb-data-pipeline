#!/usr/bin/env python3
"""
Debug Boxscore Loading Issue
"""

import sys
import json
sys.path.append('src')

from database.connection import DatabaseConnection
from database.json_to_sql_loader import JSONToSQLLoader

def debug_boxscore_loading():
    """Debug why boxscore data isn't being loaded."""
    
    print("🔍 DEBUGGING BOXSCORE LOADING")
    print("=" * 50)
    
    # Load one JSON file manually
    json_file = 'data/json/2025/05-May/combined_data_777691_20250531.json'
    print(f"Loading file: {json_file}")
    
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    print(f"✅ JSON loaded successfully")
    print(f"Game ID: {data.get('game_id')}")
    print(f"Game Date: {data.get('game_date')}")
    
    # Check boxscore structure
    boxscore = data.get('boxscore', {})
    teams = boxscore.get('teams', {})
    
    print(f"\nBoxscore structure:")
    print(f"  Teams keys: {list(teams.keys())}")
    
    for team_type in ['home', 'away']:
        team_data = teams.get(team_type, {})
        team_info = team_data.get('team', {})
        players = team_data.get('players', {})
        
        print(f"\n{team_type.upper()} team:")
        print(f"  Team ID: {team_info.get('id')}")
        print(f"  Team Name: {team_info.get('name')}")
        print(f"  Players count: {len(players)}")
        
        # Check first player with batting stats
        players_with_batting = []
        for player_key, player_data in players.items():
            if player_key.startswith('ID'):
                person = player_data.get('person', {})
                stats = player_data.get('stats', {})
                batting = stats.get('batting', {})
                
                if batting and batting.get('atBats', 0) > 0:
                    players_with_batting.append({
                        'id': person.get('id'),
                        'name': person.get('fullName'),
                        'at_bats': batting.get('atBats'),
                        'hits': batting.get('hits'),
                        'doubles': batting.get('doubles'),
                        'home_runs': batting.get('homeRuns')
                    })
        
        print(f"  Players with batting stats: {len(players_with_batting)}")
        if players_with_batting:
            print(f"  Sample player: {players_with_batting[0]}")
    
    # Now test the actual loading
    print(f"\n🧪 TESTING JSON LOADER")
    print("=" * 30)
    
    db = DatabaseConnection()
    if db.connect():
        print("✅ Connected to database")
        
        # Check before loading
        before_count = db.fetch_results("SELECT COUNT(*) FROM boxscore WHERE game_id = :game_id", 
                                      {'game_id': data.get('game_id')})[0][0]
        print(f"Boxscore records before loading: {before_count}")
        
        # Try loading
        loader = JSONToSQLLoader(db)
        try:
            result = loader._load_combined_data(data)
            print(f"Load result: {result}")
        except Exception as e:
            print(f"❌ Error during loading: {e}")
            import traceback
            traceback.print_exc()
        
        # Check after loading
        after_count = db.fetch_results("SELECT COUNT(*) FROM boxscore WHERE game_id = :game_id", 
                                     {'game_id': data.get('game_id')})[0][0]
        print(f"Boxscore records after loading: {after_count}")
        
        if after_count > before_count:
            print(f"✅ Success! Added {after_count - before_count} boxscore records")
        else:
            print("❌ No boxscore records were added")
        
        db.disconnect()
    else:
        print("❌ Failed to connect to database")

if __name__ == "__main__":
    debug_boxscore_loading()
