import json
from src.database.connection import DatabaseConnection
import pyodbc
from sqlalchemy import text

# Test with explicit transaction management using raw pyodbc
def test_hbp_with_explicit_transaction():
    # Get a file with HBP > 0
    test_file = 'data/json/2025/03-March/boxscore_raw_778499.json'
    
    with open(test_file, 'r') as f:
        data = json.load(f)
    
    # Find Gabriel Arias who should have HBP = 1
    teams = data.get('teams', {})
    gabriel_data = None
    gabriel_id = None
    
    for team_type in ['home', 'away']:
        team_data = teams.get(team_type, {})
        players = team_data.get('players', {})
        
        for player_key, player_data in players.items():
            if player_key.startswith('ID'):
                person = player_data.get('person', {})
                if 'Gabriel Arias' in person.get('fullName', ''):
                    gabriel_id = person.get('id')
                    gabriel_data = player_data.get('stats', {}).get('batting', {})
                    print(f"Found Gabriel Arias (ID: {gabriel_id})")
                    print(f"HBP in JSON: {gabriel_data.get('hitByPitch', 0)}")
                    break
    
    if gabriel_data is None:
        print("Gabriel Arias not found in this file")
        return
    
    # Now test with explicit transaction
    try:
        conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=mlb_data;Trusted_Connection=yes;'
        conn = pyodbc.connect(conn_str)
        conn.autocommit = False  # Explicit transaction control
        cursor = conn.cursor()
        
        # Build the update parameters
        params = (
            gabriel_data.get('atBats', 0),      # at_bats
            gabriel_data.get('runs', 0),        # runs  
            gabriel_data.get('hits', 0),        # hits
            gabriel_data.get('doubles', 0),     # doubles
            gabriel_data.get('triples', 0),     # triples
            gabriel_data.get('homeRuns', 0),    # home_runs
            gabriel_data.get('rbi', 0),         # rbi
            gabriel_data.get('baseOnBalls', 0), # walks
            gabriel_data.get('strikeOuts', 0),  # strikeouts
            gabriel_data.get('hitByPitch', 0),  # hit_by_pitch - this should be 1
            None,                               # game_date
            778499,                             # game_id
            gabriel_id                          # player_id
        )
        
        print(f"Updating with HBP = {gabriel_data.get('hitByPitch', 0)}")
        
        # Execute the update
        cursor.execute("""
            UPDATE boxscore SET 
                at_bats = ?, runs = ?, hits = ?, doubles = ?,
                triples = ?, home_runs = ?, rbi = ?, 
                walks = ?, strikeouts = ?, hit_by_pitch = ?, game_date = ?
            WHERE game_id = ? AND player_id = ?
        """, params)
        
        print(f"Rows affected: {cursor.rowcount}")
        
        # Check immediately in the same transaction
        cursor.execute("SELECT hit_by_pitch FROM boxscore WHERE game_id = ? AND player_id = ?", 
                      (778499, gabriel_id))
        result = cursor.fetchone()
        if result:
            print(f"Value in same transaction: {result[0]}")
        
        # Commit the transaction
        conn.commit()
        print("Transaction committed")
        
        # Check again after commit
        cursor.execute("SELECT hit_by_pitch FROM boxscore WHERE game_id = ? AND player_id = ?", 
                      (778499, gabriel_id))
        result = cursor.fetchone()
        if result:
            print(f"Value after commit: {result[0]}")
        
        cursor.close()
        conn.close()
        
        # Now check with a fresh connection
        conn2 = pyodbc.connect(conn_str)
        cursor2 = conn2.cursor()
        cursor2.execute("SELECT hit_by_pitch FROM boxscore WHERE game_id = ? AND player_id = ?", 
                       (778499, gabriel_id))
        result = cursor2.fetchone()
        if result:
            print(f"Value in fresh connection: {result[0]}")
        cursor2.close()
        conn2.close()
        
    except Exception as e:
        print(f"Error: {e}")

test_hbp_with_explicit_transaction()
