import json
import os
from pathlib import Path

# Find a sample boxscore file to check for HBP data
data_dir = Path('data')
found_file = False
for root, dirs, files in os.walk(data_dir):
    for file in files:
        if 'boxscore_raw' in file and file.endswith('.json'):
            filepath = os.path.join(root, file)
            print(f'Checking file: {filepath}')
            
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Look for HBP in batting stats
            teams = data.get('teams', {})
            for team_type in ['home', 'away']:
                team_data = teams.get(team_type, {})
                players = team_data.get('players', {})
                
                for player_key, player_data in players.items():
                    if player_key.startswith('ID'):
                        stats = player_data.get('stats', {})
                        batting = stats.get('batting', {})
                        
                        if batting:
                            player_name = player_data.get('person', {}).get('fullName', 'Unknown')
                            print(f'\nPlayer {player_name} batting stats:')
                            for key, value in batting.items():
                                print(f'  {key}: {value}')
                            
                            # Check if HBP exists
                            if 'hitByPitch' in batting:
                                print(f'  *** HBP found: {batting["hitByPitch"]} ***')
                            
                            found_file = True
                            break  # Just check one player per team
                if found_file:
                    break
            break
    if found_file:
        break

if not found_file:
    print('No boxscore files found')
