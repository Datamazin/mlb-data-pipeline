from src.database.connection import DatabaseConnection

# Test if the issue is with fetching vs updating
db = DatabaseConnection()
if db.connect():
    # First, set a known value
    print("Setting HBP to 5 for test player...")
    db.execute_query("UPDATE boxscore SET hit_by_pitch = 5 WHERE game_id = 778496 AND player_id = 645302")
    
    # Immediately check the value
    result = db.execute_query("SELECT hit_by_pitch FROM boxscore WHERE game_id = 778496 AND player_id = 645302")
    for row in result:
        print(f"Immediate check - HBP: {row.hit_by_pitch} (type: {type(row.hit_by_pitch)})")
    
    # Now test the exact UPDATE from the loader
    print("\nTesting the loader's UPDATE query...")
    
    params = {
        'game_id': 778496,
        'player_id': 645302,
        'at_bats': 5,
        'runs': 0,
        'hits': 1,
        'doubles': 1,
        'triples': 0,
        'home_runs': 0,
        'rbi': 0,
        'walks': 0,
        'strikeouts': 1,
        'hit_by_pitch': 0,
        'game_date': None
    }
    
    update_query = """
    UPDATE boxscore SET 
        at_bats = :at_bats, runs = :runs, hits = :hits, doubles = :doubles,
        triples = :triples, home_runs = :home_runs, rbi = :rbi, 
        walks = :walks, strikeouts = :strikeouts, hit_by_pitch = :hit_by_pitch, game_date = :game_date
    WHERE game_id = :game_id AND player_id = :player_id
    """
    
    result = db.execute_query(update_query, params)
    print(f"UPDATE executed, {result.rowcount} rows affected")
    
    # Check immediately after the loader's query
    result = db.execute_query("SELECT hit_by_pitch, at_bats, hits FROM boxscore WHERE game_id = 778496 AND player_id = 645302")
    for row in result:
        print(f"After loader UPDATE - HBP: {row.hit_by_pitch}, AB: {row.at_bats}, H: {row.hits}")
    
    db.disconnect()
