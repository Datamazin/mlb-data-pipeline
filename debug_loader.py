from src.database.json_to_sql_loader import JSONToSQLLoader
from src.database.connection import DatabaseConnection

# Create a custom loader that checks values immediately after update
class DebugJSONLoader(JSONToSQLLoader):
    def _insert_boxscore_stats(self, game_id, player_id, team_id, batting_stats, game_date=None):
        """Modified version that checks values after update."""
        # First try to UPDATE existing record
        update_query = """
        UPDATE boxscore SET 
            at_bats = :at_bats, runs = :runs, hits = :hits, doubles = :doubles,
            triples = :triples, home_runs = :home_runs, rbi = :rbi, 
            walks = :walks, strikeouts = :strikeouts, hit_by_pitch = :hit_by_pitch, game_date = :game_date
        WHERE game_id = :game_id AND player_id = :player_id
        """
        params = {
            'game_id': game_id,
            'player_id': player_id,
            'team_id': team_id,
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
            'game_date': game_date
        }
        
        if player_id == 645302:  # Debug Victor Robles
            print(f"DEBUG: Updating player {player_id} with HBP = {params['hit_by_pitch']}")
        
        try:
            # Execute UPDATE first
            result = self.db.execute_query(update_query, params)
            
            if player_id == 645302:  # Debug Victor Robles
                # Check immediately after update
                check_result = self.db.execute_query(
                    "SELECT hit_by_pitch, at_bats FROM boxscore WHERE game_id = :game_id AND player_id = :player_id",
                    {'game_id': game_id, 'player_id': player_id}
                )
                for row in check_result:
                    print(f"DEBUG: Immediately after UPDATE - HBP: {row.hit_by_pitch}, AB: {row.at_bats}")
            
            # Check if any rows were updated, if not, do INSERT
            if result.rowcount == 0:
                insert_query = """
                INSERT INTO boxscore (game_id, player_id, team_id, at_bats, runs, hits, doubles, triples, home_runs, rbi, walks, strikeouts, hit_by_pitch, game_date)
                VALUES (:game_id, :player_id, :team_id, :at_bats, :runs, :hits, :doubles, :triples, :home_runs, :rbi, :walks, :strikeouts, :hit_by_pitch, :game_date)
                """
                self.db.execute_query(insert_query, params)
                print(f"✅ Successfully inserted player {player_id}")
            else:
                print(f"✅ Successfully updated player {player_id}")
        except Exception as e:
            print(f"❌ Error upserting player {player_id}: {e}")
            raise

# Test with debug loader
test_file = 'data/json/2025/03-March/boxscore_raw_778496.json'
print(f'Testing with debug loader: {test_file}')

loader = DebugJSONLoader()
success = loader.load_json_to_database(test_file)

if success:
    print('\n✅ File loaded with debug loader')
    
    # Check final values in a separate connection
    db = DatabaseConnection()
    if db.connect():
        result = db.execute_query("SELECT hit_by_pitch, at_bats FROM boxscore WHERE game_id = 778496 AND player_id = 645302")
        for row in result:
            print(f"FINAL CHECK: HBP: {row.hit_by_pitch}, AB: {row.at_bats}")
        db.disconnect()
else:
    print('❌ Failed to load with debug loader')
