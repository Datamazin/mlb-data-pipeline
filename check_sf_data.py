import json

# Check the actual SF data in the file
test_file = 'data/json/2025/07-July/boxscore_raw_777064.json'

with open(test_file, 'r') as f:
    data = json.load(f)

print('Checking for SF data in the loaded file...')
teams = data.get('teams', {})

found_sf = False
for team_type in ['home', 'away']:
    team_data = teams.get(team_type, {})
    team_info = team_data.get('team', {})
    players = team_data.get('players', {})
    
    print(f'\n{team_type.upper()} team ({team_info.get("name", "Unknown")}):')
    
    for player_key, player_data in players.items():
        if player_key.startswith('ID'):
            person = player_data.get('person', {})
            stats = player_data.get('stats', {})
            batting = stats.get('batting', {})
            
            if batting:
                sf = batting.get('sacFlies', 0)
                sb = batting.get('sacBunts', 0)
                if sf > 0 or sb > 0:
                    player_name = person.get('fullName', 'Unknown')
                    player_id = person.get('id')
                    print(f'  {player_name} (ID: {player_id}): SF={sf}, SH={sb}')
                    found_sf = True

if not found_sf:
    print('\nNo SF or SH found in this file. Let me try another file with known SF data.')
    
    # Try a file from our search that definitely has SF
    test_file2 = 'data/json/2025/03-March/boxscore_raw_778496.json'  # Let's check our original test file
    
    with open(test_file2, 'r') as f:
        data2 = json.load(f)
    
    print(f'\nChecking {test_file2} for any SF data...')
    teams2 = data2.get('teams', {})
    
    # Just check one player to see the structure
    for team_type in ['home', 'away']:
        team_data = teams2.get(team_type, {})
        players = team_data.get('players', {})
        
        for player_key, player_data in players.items():
            if player_key.startswith('ID'):
                stats = player_data.get('stats', {})
                batting = stats.get('batting', {})
                
                if batting:
                    person = player_data.get('person', {})
                    player_name = person.get('fullName', 'Unknown')
                    sf = batting.get('sacFlies', 0)
                    sb = batting.get('sacBunts', 0)
                    print(f'  {player_name}: SF={sf}, SH={sb}')
                    break  # Just check first player
        break  # Just check home team
