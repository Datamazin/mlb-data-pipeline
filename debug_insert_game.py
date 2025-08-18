import json
from src.database.json_to_sql_loader import JSONToSQLLoader
from src.database.connection import DatabaseConnection

# Test with a single game to debug _insert_game method
db = DatabaseConnection()
db.connect()

loader = JSONToSQLLoader(db)

# Test file
test_file = r'data\json\2025\08-August\boxscore_raw_776697.json'

try:
    with open(test_file, 'r') as f:
        data = json.load(f)
    
    # Simulate what happens in _load_boxscore_data
    game_id = 776697
    teams_data = data.get('teams', {})
    home_team = teams_data.get('home', {}).get('team', {})
    away_team = teams_data.get('away', {}).get('team', {})
    
    print(f'🔍 Before _insert_game call:')
    print(f'  Game ID: {game_id}')
    print(f'  Home team ID: {home_team.get("id")}')
    print(f'  Away team ID: {away_team.get("id")}')
    
    # Extract game date
    game_date = data.get('gameDate')
    if game_date:
        game_date = game_date[:10]  # Extract date part
    
    # Create game data for processing
    game_data_for_processing = {
        'teams': teams_data,
        'currentInning': data.get('liveData', {}).get('linescore', {}).get('currentInning'),
        'inningState': data.get('liveData', {}).get('linescore', {}).get('inningState')
    }
    
    # Test metadata fetch
    game_metadata = loader._fetch_game_metadata_if_needed(game_id)
    print(f'  Game metadata: {game_metadata}')
    
    # Manually test _insert_game with transaction
    print('\n🧪 Testing _insert_game with transaction...')
    with db.connection.begin() as trans:
        # This simulates what happens in the loader
        loader._insert_game(game_id, game_data_for_processing, home_team, away_team, game_date, game_metadata, trans)
        print('✅ _insert_game completed')
    
    # Check the result
    result = db.execute_query('SELECT game_id, home_team_id, away_team_id, game_type FROM games WHERE game_id = ?', (game_id,))
    row = result.fetchone()
    if row:
        g_id, h_id, a_id, g_type = row
        print(f'📊 Result: Game {g_id}, Home: {h_id}, Away: {a_id}, Type: {g_type}')
    else:
        print('❌ Game not found after insert')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()

db.disconnect()
