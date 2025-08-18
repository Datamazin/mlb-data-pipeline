import json
from src.database.connection import DatabaseConnection

# Test direct update with Brady House's data
test_file = 'data/json/2025/07-July/boxscore_raw_777064.json'

with open(test_file, 'r') as f:
    data = json.load(f)

# Find Brady House's batting stats
teams = data.get('teams', {})
home_team = teams.get('home', {})
players = home_team.get('players', {})

brady_data = None
for player_key, player_data in players.items():
    if player_key.startswith('ID'):
        person = player_data.get('person', {})
        if person.get('id') == 691781:  # Brady House
            brady_data = player_data.get('stats', {}).get('batting', {})
            break

if brady_data:
    print(f'Brady House SF in JSON: {brady_data.get("sacFlies", 0)}')
    print(f'Brady House SH in JSON: {brady_data.get("sacBunts", 0)}')
    
    # Test direct database update
    db = DatabaseConnection()
    if db.connect():
        # Direct update with the exact values
        params = {
            'game_id': 777064,
            'player_id': 691781,
            'at_bats': brady_data.get('atBats', 0),
            'runs': brady_data.get('runs', 0),
            'hits': brady_data.get('hits', 0),
            'doubles': brady_data.get('doubles', 0),
            'triples': brady_data.get('triples', 0),
            'home_runs': brady_data.get('homeRuns', 0),
            'rbi': brady_data.get('rbi', 0),
            'walks': brady_data.get('baseOnBalls', 0),
            'strikeouts': brady_data.get('strikeOuts', 0),
            'hit_by_pitch': brady_data.get('hitByPitch', 0),
            'sacrifice_flies': brady_data.get('sacFlies', 0),
            'sacrifice_bunts': brady_data.get('sacBunts', 0),
            'game_date': None
        }
        
        print(f'\nUpdating with SF={params["sacrifice_flies"]}, SH={params["sacrifice_bunts"]}')
        
        update_query = """
            UPDATE boxscore SET 
                at_bats = :at_bats, runs = :runs, hits = :hits, doubles = :doubles,
                triples = :triples, home_runs = :home_runs, rbi = :rbi, 
                walks = :walks, strikeouts = :strikeouts, hit_by_pitch = :hit_by_pitch, 
                sacrifice_flies = :sacrifice_flies, sacrifice_bunts = :sacrifice_bunts, game_date = :game_date
            WHERE game_id = :game_id AND player_id = :player_id
        """
        
        result = db.execute_query(update_query, params)
        print(f'Update affected {result.rowcount} rows')
        
        # Immediately check the result
        check_result = db.execute_query(
            'SELECT sacrifice_flies, sacrifice_bunts FROM boxscore WHERE game_id = 777064 AND player_id = 691781'
        )
        for row in check_result:
            print(f'Immediate check: SF={row.sacrifice_flies}, SH={row.sacrifice_bunts}')
        
        db.disconnect()
else:
    print('Brady House data not found')
