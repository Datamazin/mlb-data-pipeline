import json
from src.database.connection import DatabaseConnection

# Load the test file and examine the HBP data
test_file = 'data/json/2025/03-March/boxscore_raw_778496.json'

with open(test_file, 'r') as f:
    data = json.load(f)

# Look for HBP values in the data
teams = data.get('teams', {})
print("HBP values found in JSON:")

for team_type in ['home', 'away']:
    team_data = teams.get(team_type, {})
    team_info = team_data.get('team', {})
    players = team_data.get('players', {})
    
    print(f"\n{team_type.upper()} team ({team_info.get('name', 'Unknown')}):")
    
    for player_key, player_data in players.items():
        if player_key.startswith('ID'):
            person = player_data.get('person', {})
            stats = player_data.get('stats', {})
            batting = stats.get('batting', {})
            
            if batting:
                player_name = person.get('fullName', 'Unknown')
                player_id = person.get('id')
                hbp_value = batting.get('hitByPitch', 0)
                
                print(f"  {player_name} (ID: {player_id}): HBP = {hbp_value} (type: {type(hbp_value)})")

# Now let's manually test the update with specific values
print("\n" + "="*50)
print("Testing manual database update:")

db = DatabaseConnection()
if db.connect():
    # Test direct update with a specific player
    test_player_id = 645302  # Victor Robles from the JSON
    
    # First, get current values
    result = db.execute_query('SELECT hit_by_pitch FROM boxscore WHERE game_id = 778496 AND player_id = :player_id', 
                             {'player_id': test_player_id})
    for row in result:
        print(f"Current HBP for player {test_player_id}: {row.hit_by_pitch}")
    
    # Update with a test value
    try:
        result = db.execute_query("""
            UPDATE boxscore SET hit_by_pitch = :hbp_value 
            WHERE game_id = :game_id AND player_id = :player_id
        """, {
            'hbp_value': 0,  # From JSON data
            'game_id': 778496,
            'player_id': test_player_id
        })
        print(f"Update affected {result.rowcount} rows")
        
        # Check the result
        result = db.execute_query('SELECT hit_by_pitch FROM boxscore WHERE game_id = 778496 AND player_id = :player_id', 
                                 {'player_id': test_player_id})
        for row in result:
            print(f"Updated HBP for player {test_player_id}: {row.hit_by_pitch}")
            
    except Exception as e:
        print(f"Error in manual update: {e}")
    
    db.disconnect()
