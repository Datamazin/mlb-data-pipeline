#!/usr/bin/env python3
"""
Repair May 2025 walks data by reprocessing JSON files from the correct location.
The original repair operation was looking in the wrong directory.
"""

import os
import sys
import json
import glob
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database.connection import DatabaseConnection

class MayWalksRepairer:
    def __init__(self):
        self.db = DatabaseConnection()
        self.json_directory = "C:/Users/metsy/source/repos/mlb-data-pipeline/data/json/2025/05-May"
        self.updated_count = 0
        self.processed_games = 0
        self.total_walks_added = 0
        
    def repair_may_walks(self):
        """Repair May 2025 walks data by reprocessing JSON files."""
        print("🔧 Starting May 2025 Walks Repair Operation")
        print("=" * 60)
        
        if not self.db.connect():
            print("❌ Failed to connect to database")
            return False
        
        try:
            # Get all combined_data JSON files for May 2025
            json_pattern = os.path.join(self.json_directory, "combined_data_*.json")
            json_files = glob.glob(json_pattern)
            
            if not json_files:
                print(f"❌ No JSON files found in {self.json_directory}")
                return False
            
            print(f"📁 Found {len(json_files)} May 2025 JSON files to process")
            print()
            
            # Process each file
            for i, json_file in enumerate(json_files, 1):
                try:
                    self._process_json_file(json_file)
                    
                    # Progress update every 50 games
                    if i % 50 == 0:
                        print(f"📈 Progress: {i}/{len(json_files)} files processed")
                        print(f"   Updated {self.updated_count} player records")
                        print(f"   Added {self.total_walks_added} total walks")
                        print()
                        
                except Exception as e:
                    print(f"❌ Error processing {os.path.basename(json_file)}: {e}")
                    continue
            
            # Final summary
            print("🎉 May 2025 Walks Repair Complete!")
            print("=" * 60)
            print(f"📊 Final Statistics:")
            print(f"   Files processed: {len(json_files)}")
            print(f"   Games processed: {self.processed_games}")
            print(f"   Player records updated: {self.updated_count}")
            print(f"   Total walks added: {self.total_walks_added}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during repair operation: {e}")
            return False
        finally:
            self.db.disconnect()
    
    def _process_json_file(self, json_file_path):
        """Process a single JSON file and update walks data."""
        try:
            with open(json_file_path, 'r') as f:
                data = json.load(f)
            
            game_id = data.get('game_id')
            if not game_id:
                return
            
            boxscore = data.get('boxscore', {})
            if not boxscore:
                return
            
            teams = boxscore.get('teams', {})
            game_updated = False
            
            # Process both home and away teams
            for team_type in ['home', 'away']:
                team_data = teams.get(team_type, {})
                team_info = team_data.get('team', {})
                players = team_data.get('players', {})
                team_id = team_info.get('id')
                
                if not team_id:
                    continue
                
                # Process each player
                for player_key, player_data in players.items():
                    if not player_key.startswith('ID'):
                        continue
                    
                    person = player_data.get('person', {})
                    stats = player_data.get('stats', {})
                    batting = stats.get('batting', {})
                    
                    player_id = person.get('id')
                    if not player_id:
                        continue
                    
                    # Extract walks data
                    walks = batting.get('baseOnBalls', 0)
                    stolen_bases = batting.get('stolenBases', 0)
                    caught_stealing = batting.get('caughtStealing', 0)
                    
                    # Update the database record
                    if self._update_player_walks(game_id, player_id, walks, stolen_bases, caught_stealing):
                        if walks > 0 or stolen_bases > 0 or caught_stealing > 0:
                            self.updated_count += 1
                            self.total_walks_added += walks
                            game_updated = True
            
            if game_updated:
                self.processed_games += 1
                
        except Exception as e:
            print(f"❌ Error processing file {json_file_path}: {e}")
            raise
    
    def _update_player_walks(self, game_id, player_id, walks, stolen_bases, caught_stealing):
        """Update walks, stolen bases, and caught stealing for a specific player."""
        try:
            # Update the existing boxscore record
            query = """
            UPDATE boxscore 
            SET walks = :walks, 
                stolen_bases = :stolen_bases, 
                caught_stealing = :caught_stealing
            WHERE game_id = :game_id 
            AND player_id = :player_id
            """
            
            params = {
                'walks': walks,
                'stolen_bases': stolen_bases,
                'caught_stealing': caught_stealing,
                'game_id': game_id,
                'player_id': player_id
            }
            
            result = self.db.execute_query(query, params)
            return True
            
        except Exception as e:
            print(f"❌ Error updating walks for player {player_id} in game {game_id}: {e}")
            return False

def main():
    """Main function to run the May walks repair."""
    repairer = MayWalksRepairer()
    success = repairer.repair_may_walks()
    
    if success:
        print("\n✅ May 2025 walks repair completed successfully!")
        print("🔍 Run a verification query to confirm the repair worked.")
    else:
        print("\n❌ May 2025 walks repair failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
