import json
from src.database.connection import DatabaseConnection

# Test the exact parameter values being used in the loader
test_file = 'data/json/2025/03-March/boxscore_raw_778496.json'

with open(test_file, 'r') as f:
    data = json.load(f)

# Get the batting stats for Victor Robles to test with
teams = data.get('teams', {})
home_team = teams.get('home', {})
players = home_team.get('players', {})

# Find Victor Robles (player ID 645302)
for player_key, player_data in players.items():
    if player_key.startswith('ID'):
        person = player_data.get('person', {})
        if person.get('id') == 645302:  # Victor Robles
            stats = player_data.get('stats', {})
            batting_stats = stats.get('batting', {})
            
            print(f"Found Victor Robles batting stats:")
            for key, value in batting_stats.items():
                print(f"  {key}: {value} (type: {type(value)})")
            
            # Create the exact parameters that would be used in the loader
            params = {
                'game_id': 778496,
                'player_id': person.get('id'),
                'team_id': 136,  # Seattle Mariners
                'at_bats': batting_stats.get('atBats', 0),
                'runs': batting_stats.get('runs', 0),
                'hits': batting_stats.get('hits', 0),
                'doubles': batting_stats.get('doubles', 0),
                'triples': batting_stats.get('triples', 0),
                'home_runs': batting_stats.get('homeRuns', 0),
                'rbi': batting_stats.get('rbi', 0),
                'walks': batting_stats.get('baseOnBalls', 0),
                'strikeouts': batting_stats.get('strikeOuts', 0),
                'hit_by_pitch': batting_stats.get('hitByPitch', 0),
                'game_date': None
            }
            
            print(f"\nParameters to be used:")
            for key, value in params.items():
                print(f"  {key}: {value} (type: {type(value)})")
            
            # Test the exact UPDATE query
            db = DatabaseConnection()
            if db.connect():
                update_query = """
                UPDATE boxscore SET 
                    at_bats = :at_bats, runs = :runs, hits = :hits, doubles = :doubles,
                    triples = :triples, home_runs = :home_runs, rbi = :rbi, 
                    walks = :walks, strikeouts = :strikeouts, hit_by_pitch = :hit_by_pitch, game_date = :game_date
                WHERE game_id = :game_id AND player_id = :player_id
                """
                
                print(f"\nExecuting UPDATE query...")
                try:
                    result = db.execute_query(update_query, params)
                    print(f"✅ UPDATE executed, {result.rowcount} rows affected")
                    
                    # Immediately check the result
                    check_query = "SELECT hit_by_pitch, walks, at_bats FROM boxscore WHERE game_id = :game_id AND player_id = :player_id"
                    result = db.execute_query(check_query, {'game_id': 778496, 'player_id': 645302})
                    for row in result:
                        print(f"Immediately after update - HBP: {row.hit_by_pitch}, BB: {row.walks}, AB: {row.at_bats}")
                    
                except Exception as e:
                    print(f"❌ Error in UPDATE: {e}")
                
                db.disconnect()
            
            break
