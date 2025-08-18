#!/usr/bin/env python3
"""
Fix missing game_type data by fetching game metadata from MLB API.
This script will identify games with blank game_type and update them using the MLB Stats API.
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
        
        # Fallback: Try the game feed endpoint
        url = f"https://statsapi.mlb.com/api/v1/game/{game_id}/feed/live"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            if 'gameData' in data and 'game' in data['gameData']:
                return data['gameData']['game'].get('gameType')
        
        print(f"❌ Could not fetch game type for game {game_id} (HTTP {response.status_code})")
        return None
        
    except Exception as e:
        print(f"❌ Error fetching game type for game {game_id}: {e}")
        return None

def fix_missing_game_types():
    """Fix missing game_type data for all games in the database."""
    print("🔧 Starting game type fix process...")
    
    db = DatabaseConnection()
    if not db.connect():
        print("❌ Failed to connect to database")
        return
    
    try:
        # Get all games with missing game_type
        result = db.execute_query("""
            SELECT game_id, game_date 
            FROM games 
            WHERE game_type IS NULL OR game_type = '' 
            ORDER BY game_date DESC
        """)
        
        games_to_fix = []
        for row in result:
            games_to_fix.append((row.game_id, row.game_date))
        
        print(f"📊 Found {len(games_to_fix)} games with missing game_type")
        
        if not games_to_fix:
            print("✅ No games need fixing!")
            return
        
        # Process games in batches to avoid overwhelming the API
        updated_count = 0
        error_count = 0
        
        for i, (game_id, game_date) in enumerate(games_to_fix):
            print(f"🔄 Processing game {game_id} ({i+1}/{len(games_to_fix)}) - {game_date}")
            
            # Fetch game type from API
            game_type = fetch_game_type_from_api(game_id)
            
            if game_type:
                # Update database
                try:
                    db.execute_query(
                        "UPDATE games SET game_type = :game_type WHERE game_id = :game_id",
                        {'game_type': game_type, 'game_id': game_id}
                    )
                    updated_count += 1
                    print(f"✅ Updated game {game_id} with game_type: {game_type}")
                except Exception as e:
                    error_count += 1
                    print(f"❌ Failed to update game {game_id} in database: {e}")
            else:
                error_count += 1
                print(f"❌ Could not fetch game_type for game {game_id}")
            
            # Rate limiting to be respectful to the API
            if i % 10 == 0 and i > 0:
                print(f"⏸️ Taking a brief pause after {i} games...")
                time.sleep(2)
            else:
                time.sleep(0.5)  # Half second between requests
        
        print(f"\n✅ Game type fix complete!")
        print(f"📊 Updated: {updated_count} games")
        print(f"❌ Errors: {error_count} games")
        
        # Show final statistics
        result = db.execute_query("""
            SELECT game_type, COUNT(*) as count 
            FROM games 
            GROUP BY game_type 
            ORDER BY count DESC
        """)
        
        print(f"\n📈 Final Game Type Distribution:")
        for row in result:
            game_type_display = 'NULL/Empty' if (row.game_type is None or row.game_type == '') else row.game_type
            print(f"   {game_type_display}: {row.count}")
        
    except Exception as e:
        print(f"❌ Error during game type fix: {e}")
    
    finally:
        db.disconnect()

if __name__ == "__main__":
    fix_missing_game_types()
