#!/usr/bin/env python3
"""
Test script to fix game_type for just a few games first.
"""

import requests
import time
from src.database.connection import DatabaseConnection

def fetch_game_type_from_api(game_id):
    """Fetch game type from MLB Stats API."""
    try:
        # Try the schedule endpoint first (more reliable for game metadata)
        url = f"https://statsapi.mlb.com/api/v1/schedule?gamePk={game_id}&hydrate=game"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            if 'dates' in data and data['dates']:
                for date_entry in data['dates']:
                    if 'games' in date_entry:
                        for game in date_entry['games']:
                            if game.get('gamePk') == game_id:
                                return game.get('gameType')
        
        print(f"❌ Could not fetch game type for game {game_id} (HTTP {response.status_code})")
        return None
        
    except Exception as e:
        print(f"❌ Error fetching game type for game {game_id}: {e}")
        return None

def test_fix_game_types():
    """Test fixing game_type for just a few games."""
    print("🔧 Testing game type fix for a few games...")
    
    db = DatabaseConnection()
    if not db.connect():
        print("❌ Failed to connect to database")
        return
    
    try:
        # Get just the first 5 games with missing game_type
        result = db.execute_query("""
            SELECT TOP 5 game_id, game_date 
            FROM games 
            WHERE game_type IS NULL OR game_type = '' 
            ORDER BY game_date DESC
        """)
        
        games_to_fix = []
        for row in result:
            games_to_fix.append((row.game_id, row.game_date))
        
        print(f"📊 Testing with {len(games_to_fix)} games")
        
        for i, (game_id, game_date) in enumerate(games_to_fix):
            print(f"🔄 Processing game {game_id} - {game_date}")
            
            # Fetch game type from API
            game_type = fetch_game_type_from_api(game_id)
            
            if game_type:
                # Update database
                update_result = db.execute_with_transaction(
                    "UPDATE games SET game_type = :game_type WHERE game_id = :game_id",
                    {'game_type': game_type, 'game_id': game_id}
                )
                
                if update_result:
                    print(f"✅ Updated game {game_id} with game_type: {game_type}")
                else:
                    print(f"❌ Failed to update game {game_id} in database")
            else:
                print(f"❌ Could not fetch game_type for game {game_id}")
            
            time.sleep(1)  # Be respectful to the API
        
        # Check the results
        print("\n📊 Checking updated games:")
        for game_id, _ in games_to_fix:
            result = db.execute_query("SELECT game_id, game_type FROM games WHERE game_id = :game_id", {'game_id': game_id})
            for row in result:
                print(f"  Game {row.game_id}: game_type = '{row.game_type}'")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
    
    finally:
        db.disconnect()

if __name__ == "__main__":
    test_fix_game_types()
