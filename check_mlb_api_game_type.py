#!/usr/bin/env python3
"""
Check MLB API for Game Type Information
"""

import requests
import json

def check_mlb_api_game_type():
    """Check if MLB API provides game type information."""
    
    print("🔍 CHECKING MLB API FOR GAME TYPE INFO")
    print("=" * 50)
    
    # Test with a recent date to get sample game data
    base_url = "https://statsapi.mlb.com/api/v1"
    
    # Get schedule for a sample date
    print("1. Checking schedule endpoint...")
    schedule_url = f"{base_url}/schedule"
    params = {
        'startDate': '2025-04-15',
        'endDate': '2025-04-15',
        'sportId': 1,
        'hydrate': 'team,linescore,game'
    }
    
    try:
        response = requests.get(schedule_url, params=params)
        if response.status_code == 200:
            schedule_data = response.json()
            
            if schedule_data.get('dates'):
                games = schedule_data['dates'][0].get('games', [])
                if games:
                    sample_game = games[0]
                    print(f"   Sample game keys: {list(sample_game.keys())}")
                    
                    # Check for game type fields
                    game_type_fields = [k for k in sample_game.keys() if 'type' in k.lower()]
                    print(f"   Game type fields: {game_type_fields}")
                    
                    # Check if gameType exists
                    if 'gameType' in sample_game:
                        print(f"   ✅ gameType found: {sample_game['gameType']}")
                    else:
                        print(f"   ❌ gameType not found in schedule")
                    
                    # Show all simple fields
                    print(f"   Sample game data:")
                    for key, value in sample_game.items():
                        if isinstance(value, (str, int, bool)) or value is None:
                            print(f"     {key}: {value}")
                        
        print(f"\n2. Checking game feed endpoint...")
        # Get a specific game's feed
        if games:
            game_id = games[0]['gamePk']
            feed_url = f"{base_url}/game/{game_id}/feed/live"
            
            response = requests.get(feed_url)
            if response.status_code == 200:
                feed_data = response.json()
                
                # Check top level
                print(f"   Feed top-level keys: {list(feed_data.keys())}")
                
                # Check gameData section
                if 'gameData' in feed_data:
                    game_data = feed_data['gameData']
                    print(f"   GameData keys: {list(game_data.keys())}")
                    
                    # Check game section
                    if 'game' in game_data:
                        game_info = game_data['game']
                        print(f"   Game info keys: {list(game_info.keys())}")
                        
                        if 'type' in game_info:
                            print(f"   ✅ Game type found: {game_info['type']}")
                        else:
                            print(f"   ❌ Game type not found in game info")
                            
                        # Show all simple fields in game info
                        print(f"   Game info data:")
                        for key, value in game_info.items():
                            if isinstance(value, (str, int, bool)) or value is None:
                                print(f"     {key}: {value}")
                            elif isinstance(value, dict) and key == 'type':
                                print(f"     {key}: {value}")
        
    except Exception as e:
        print(f"❌ Error checking MLB API: {e}")

if __name__ == "__main__":
    check_mlb_api_game_type()
