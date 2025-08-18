import json

# Test file
test_file = r'data\json\2025\08-August\boxscore_raw_776697.json'

try:
    with open(test_file, 'r') as f:
        data = json.load(f)
    
    # Extract teams data like the loader does
    teams_data = data.get('teams', {})
    print('📊 Teams data structure:')
    print(f'  Teams keys: {list(teams_data.keys())}')
    
    if 'home' in teams_data:
        home_team = teams_data['home'].get('team', {})
        print(f'  Home team ID: {home_team.get("id")}')
        print(f'  Home team name: {home_team.get("name")}')
        
    if 'away' in teams_data:
        away_team = teams_data['away'].get('team', {})
        print(f'  Away team ID: {away_team.get("id")}')
        print(f'  Away team name: {away_team.get("name")}')
        
    # Test the exact data structure that gets passed to _process_game_data
    game_data_for_processing = {
        'teams': teams_data,  # Include full team data from boxscore
        'currentInning': data.get('liveData', {}).get('linescore', {}).get('currentInning'),
        'inningState': data.get('liveData', {}).get('linescore', {}).get('inningState')
    }
    
    print('\n🔍 Processing in _process_game_data:')
    game_data = game_data_for_processing
    teams_data_proc = game_data.get('teams', {})
    home_team = teams_data_proc.get('home', {}).get('team', {})
    away_team = teams_data_proc.get('away', {}).get('team', {})
    
    print(f'  Home team extracted: {home_team.get("id")}')
    print(f'  Away team extracted: {away_team.get("id")}')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
