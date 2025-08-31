#!/usr/bin/env python3
"""
Debug MLB data structure for CSV export
"""
import os
import sys
import json
from datetime import date

sys.path.append('src')
from etl.extract import get_games_for_date
from api.mlb_client import MLBClient

def debug_data_structure():
    """Debug the actual data structure returned by our API."""
    print("🔍 MLB Data Structure Debug")
    print("=" * 40)
    
    client = MLBClient()
    today = date.today()
    
    # Get one game
    games_schedule = get_games_for_date(today)
    if not games_schedule:
        print("❌ No games found")
        return
    
    game_info = games_schedule[0]
    game_id = game_info['gamePk']
    
    print(f"🎯 Analyzing Game {game_id}")
    print(f"Game info keys: {list(game_info.keys())}")
    
    # Get detailed data
    try:
        boxscore_data = client.fetch_boxscore(game_id)
        game_data = client.fetch_game_data(game_id)
        
        print(f"\n📊 Boxscore data keys: {list(boxscore_data.keys()) if boxscore_data else 'None'}")
        print(f"🎮 Game data keys: {list(game_data.keys()) if game_data else 'None'}")
        
        # Save sample to file for inspection
        sample_data = {
            'schedule_info': game_info,
            'boxscore_data': boxscore_data,
            'game_data': game_data
        }
        
        with open('debug_sample.json', 'w') as f:
            json.dump(sample_data, f, indent=2, default=str)
        
        print(f"\n💾 Sample data saved to debug_sample.json")
        
        # Show structure
        if game_data:
            print(f"\n🏟️  Game structure:")
            print(f"   - Game ID: {game_data.get('gamePk', 'Missing')}")
            print(f"   - Teams: {list(game_data.get('teams', {}).keys())}")
            print(f"   - Status: {game_data.get('status', {}).get('detailedState', 'Missing')}")
            
        if boxscore_data:
            print(f"\n📊 Boxscore structure:")
            print(f"   - Teams: {list(boxscore_data.get('teams', {}).keys())}")
            if 'teams' in boxscore_data:
                home_players = boxscore_data['teams'].get('home', {}).get('players', {})
                print(f"   - Home players: {len(home_players)} found")
                if home_players:
                    first_player_key = list(home_players.keys())[0]
                    first_player = home_players[first_player_key]
                    print(f"   - Sample player keys: {list(first_player.keys())}")
                    batting_stats = first_player.get('stats', {}).get('batting', {})
                    if batting_stats:
                        print(f"   - Batting stats keys: {list(batting_stats.keys())}")
                        print(f"   - Stolen bases: {batting_stats.get('stolenBases', 'Missing')}")
                        print(f"   - Caught stealing: {batting_stats.get('caughtStealing', 'Missing')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_data_structure()
