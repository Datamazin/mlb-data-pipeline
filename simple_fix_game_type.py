#!/usr/bin/env python3
"""
Fix game_type using a simple approach that works with SQLAlchemy transactions.
"""

import requests
import time
from sqlalchemy import text, create_engine
from src.database.connection import DatabaseConnection

def fetch_game_type_from_api(game_id):
    """Fetch game type from MLB Stats API."""
    try:
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
        return None
        
    except Exception as e:
        print(f"❌ Error fetching game type for game {game_id}: {e}")
        return None

def simple_fix_game_types():
    """Fix game_type for games using simple approach."""
    print("🔧 Simple fix for game types...")
    
    db = DatabaseConnection()
    if not db.connect():
        print("❌ Failed to connect to database")
        return
    
    try:
        # Get games to fix (separate connection for reading)
        with db.connection.begin() as trans:
            result = db.connection.execute(text("""
                SELECT TOP 20 game_id, game_date 
                FROM games 
                WHERE game_type IS NULL OR game_type = '' 
                ORDER BY game_date DESC
            """))
            games_to_fix = [(row.game_id, row.game_date) for row in result]
        
        print(f"📊 Found {len(games_to_fix)} games to fix")
        
        updated_count = 0
        
        for i, (game_id, game_date) in enumerate(games_to_fix):
            print(f"🔄 [{i+1}/{len(games_to_fix)}] Processing game {game_id} - {game_date}")
            
            game_type = fetch_game_type_from_api(game_id)
            
            if game_type:
                try:
                    # Create fresh connection for each update to avoid transaction conflicts
                    fresh_db = DatabaseConnection()
                    if fresh_db.connect():
                        with fresh_db.connection.begin():
                            fresh_db.connection.execute(
                                text("UPDATE games SET game_type = :game_type WHERE game_id = :game_id"),
                                {'game_type': game_type, 'game_id': game_id}
                            )
                        fresh_db.disconnect()
                        updated_count += 1
                        print(f"✅ Updated game {game_id} with game_type: {game_type}")
                except Exception as e:
                    print(f"❌ Database error for game {game_id}: {e}")
            else:
                print(f"❌ Could not fetch game_type for game {game_id}")
            
            time.sleep(0.5)  # Rate limiting
        
        print(f"\n✅ Simple fix complete! Updated {updated_count} games.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        db.disconnect()

if __name__ == "__main__":
    simple_fix_game_types()
