#!/usr/bin/env python3
"""
Test MLB API Schedule Response to Find Game Type Information
"""

import os
import sys
import json
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from api.mlb_client import MLBClient

def test_schedule_api():
    """Test the MLB schedule API to see what game type information is available."""
    client = MLBClient()
    
    try:
        # Test with March 2025 data when we have spring training games
        print("Fetching schedule data for March 4, 2025...")
        schedule_data = client.fetch_schedule('2025-03-04', '2025-03-04')
        
        # Save the raw response for analysis
        with open('schedule_test_response.json', 'w') as f:
            json.dump(schedule_data, f, indent=2)
        
        print("✅ Schedule data saved to schedule_test_response.json")
        
        # Look for game type information
        dates = schedule_data.get('dates', [])
        
        for date_entry in dates:
            games = date_entry.get('games', [])
            for game in games:
                game_id = game.get('gamePk')
                print(f"\n🎮 Game ID: {game_id}")
                
                # Look for game type indicators
                game_type = game.get('gameType')
                series_description = game.get('seriesDescription')
                game_date = game.get('gameDate')
                status = game.get('status', {}).get('statusCode')
                
                print(f"   Game Type: {game_type}")
                print(f"   Series Description: {series_description}")
                print(f"   Game Date: {game_date}")
                print(f"   Status: {status}")
                
                # Check teams for spring training indicators
                away_team = game.get('teams', {}).get('away', {}).get('team', {})
                home_team = game.get('teams', {}).get('home', {}).get('team', {})
                
                away_spring_league = away_team.get('springLeague', {})
                home_spring_league = home_team.get('springLeague', {})
                
                if away_spring_league:
                    print(f"   Away Spring League: {away_spring_league.get('name')} ({away_spring_league.get('abbreviation')})")
                
                if home_spring_league:
                    print(f"   Home Spring League: {home_spring_league.get('name')} ({home_spring_league.get('abbreviation')})")
                
                # Check for venue information
                venue = game.get('venue', {})
                print(f"   Venue: {venue.get('name')}")
                
                # Look for other potential indicators
                print(f"   All available fields: {list(game.keys())}")
                
                if game_id == 779011:  # Our test game
                    print(f"\n📋 Detailed info for game {game_id}:")
                    print(json.dumps(game, indent=2))
                    break
        
        print(f"\n✅ Analysis complete. Check schedule_test_response.json for full details.")
        
    except Exception as e:
        print(f"❌ Error testing schedule API: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_schedule_api()
    if success:
        print("\n✅ Schedule API test completed!")
    else:
        print("\n❌ Schedule API test failed!")
