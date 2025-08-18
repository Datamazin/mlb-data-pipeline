from src.database.connection import DatabaseConnection

# Test if our connection class is working properly with the new columns
db = DatabaseConnection()
if db.connect():
    # First, manually set Freddie Freeman's SF to 2 (he should have 2 from the JSON)
    update_result = db.execute_with_transaction("""
        UPDATE boxscore SET sacrifice_flies = 2, sacrifice_bunts = 0 
        WHERE game_id = 776858 AND player_id = 518692
    """)
    print(f"Manual update affected {update_result.rowcount} rows")
    
    # Immediately check within the same connection
    result = db.execute_query("""
        SELECT sacrifice_flies, sacrifice_bunts 
        FROM boxscore 
        WHERE game_id = 776858 AND player_id = 518692
    """)
    
    for row in result:
        print(f"Same connection check: SF={row.sacrifice_flies}, SH={row.sacrifice_bunts}")
    
    db.disconnect()

# Now check with a fresh connection
db2 = DatabaseConnection()
if db2.connect():
    result = db2.execute_query("""
        SELECT sacrifice_flies, sacrifice_bunts 
        FROM boxscore 
        WHERE game_id = 776858 AND player_id = 518692
    """)
    
    for row in result:
        print(f"Fresh connection check: SF={row.sacrifice_flies}, SH={row.sacrifice_bunts}")
    
    db2.disconnect()

# Also check the total count
db3 = DatabaseConnection()
if db3.connect():
    result = db3.execute_query("SELECT COUNT(*) as sf_count FROM boxscore WHERE sacrifice_flies > 0")
    for row in result:
        print(f"Total players with SF > 0: {row.sf_count}")
    
    db3.disconnect()
