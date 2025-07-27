#!/usr/bin/env python3
"""
Test Regular Season vs Spring Training Game Types
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from api.mlb_client import MLBClient

def test_game_types():
    """Test different game types to understand the patterns."""
    client = MLBClient()
    
    print("🌸 SPRING TRAINING GAMES (March 2025):")
    print("=" * 50)
    spring_data = client.fetch_schedule('2025-03-04', '2025-03-04')
    
    for date_entry in spring_data.get('dates', []):
        for game in date_entry.get('games', [])[:3]:  # First 3 games
            game_id = game.get('gamePk')
            game_type = game.get('gameType')
            series_description = game.get('seriesDescription')
            spring_league = game.get('teams', {}).get('home', {}).get('team', {}).get('springLeague', {})
            
            print(f"Game {game_id}: Type='{game_type}', Series='{series_description}'")
            if spring_league:
                print(f"  └─ Spring League: {spring_league.get('name')} ({spring_league.get('abbreviation')})")
    
    print("\n⚾ REGULAR SEASON GAMES (April 2024):")
    print("=" * 50)
    
    # Test regular season
    regular_data = client.fetch_schedule('2024-04-15', '2024-04-15')
    
    for date_entry in regular_data.get('dates', []):
        for game in date_entry.get('games', [])[:3]:  # First 3 games
            game_id = game.get('gamePk')
            game_type = game.get('gameType')
            series_description = game.get('seriesDescription')
            
            print(f"Game {game_id}: Type='{game_type}', Series='{series_description}'")
    
    print("\n🏆 POSTSEASON GAMES (October 2024):")
    print("=" * 50)
    
    # Test postseason
    postseason_data = client.fetch_schedule('2024-10-15', '2024-10-15')
    
    for date_entry in postseason_data.get('dates', []):
        for game in date_entry.get('games', [])[:3]:  # First 3 games
            game_id = game.get('gamePk')
            game_type = game.get('gameType')
            series_description = game.get('seriesDescription')
            
            print(f"Game {game_id}: Type='{game_type}', Series='{series_description}'")
    
    print("\n📋 GAME TYPE SUMMARY:")
    print("=" * 50)
    print("S = Spring Training / Preseason")
    print("R = Regular Season")
    print("F = Wild Card / First Round")
    print("D = Division Series")
    print("L = League Championship Series")
    print("W = World Series")
    print("A = All-Star Game")

if __name__ == "__main__":
    test_game_types()
