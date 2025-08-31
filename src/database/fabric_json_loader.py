import json
import os
from datetime import datetime
from pathlib import Path
from src.database.fabric_connection import FabricConnection
from src.utils.json_handler import load_from_json

class FabricJSONLoader:
    def __init__(self, fabric_connection=None):
        """
        Initialize the JSON to Fabric loader.
        
        Args:
            fabric_connection: FabricConnection instance (optional)
        """
        self.db = fabric_connection or FabricConnection()

    def load_json_to_database(self, json_file_path):
        """
        Load data from a JSON file into the Fabric database.
        
        Args:
            json_file_path: Path to the JSON file
        """
        try:
            # Load JSON data
            data = load_from_json(json_file_path)
            if not data:
                print("❌ Failed to load JSON data")
                return False

            # Connect to database
            if not self.db.connect():
                print("❌ Failed to connect to Fabric")
                return False

            # Determine the type of JSON file and process accordingly
            if 'combined_data' in str(json_file_path):
                return self._load_combined_data(data)
            elif 'boxscore_raw' in str(json_file_path):
                # Extract game_id from filename for boxscore files
                game_id = self._extract_game_id_from_filename(json_file_path)
                return self._load_boxscore_data(data, game_id)
            elif 'game_raw' in str(json_file_path):
                return self._load_game_data(data)
            else:
                print(f"❌ Unknown JSON file type: {json_file_path}")
                return False

        except Exception as e:
            print(f"❌ Error loading JSON to Fabric: {e}")
            return False
        finally:
            self.db.disconnect()

    def _load_combined_data(self, data):
        """Load combined JSON data (contains both boxscore and game data)."""
        try:
            game_id = data.get('game_id')
            game_date = data.get('game_date')  # Extract the actual game date
            
            # Extract metadata from combined data
            game_metadata = {
                'game_type': data.get('game_type'),
                'official_date': data.get('official_date'),
                'series_description': data.get('series_description')
            }
            
            # Use a transaction to ensure all data is committed together
            queries = []
            
            # First, save raw JSON data for backup
            queries.append(self._prepare_raw_json_query(game_id, 'combined', json.dumps(data)))
            
            # Extract and load game data with proper date and metadata
            if 'game_data' in data:
                game_queries = self._prepare_game_data_queries(game_id, data['game_data'], game_date, game_metadata)
                queries.extend(game_queries)
            
            # Extract and load boxscore data
            if 'boxscore' in data:
                boxscore_queries = self._prepare_boxscore_data_queries(game_id, data['boxscore'], game_date)
                queries.extend(boxscore_queries)
            
            # Execute all queries in a transaction
            self.db.execute_transaction(queries)
            
            print(f"✅ Successfully loaded combined data for game {game_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error processing combined data: {e}")
            return False

    def _extract_game_id_from_filename(self, filename):
        """Extract game ID from filename like 'boxscore_raw_776762.json'."""
        try:
            import os
            filename_only = os.path.basename(str(filename))
            if '_' in filename_only:
                parts = filename_only.split('_')
                if len(parts) >= 3:
                    # Extract number from last part before .json
                    game_id_part = parts[-1].replace('.json', '')
                    if game_id_part.isdigit():
                        return int(game_id_part)
        except Exception as e:
            print(f"❌ Error extracting game_id from filename {filename}: {e}")
        return None

    def _fetch_game_metadata_if_needed(self, game_id):
        """Fetch game metadata from MLB schedule API if needed."""
        try:
            if not hasattr(self, 'mlb_client'):
                from src.api.mlb_client import MLBClient
                self.mlb_client = MLBClient()
            
            print(f"🔍 Fetching game metadata for game {game_id}...")
            metadata = self.mlb_client.fetch_game_metadata(game_id)
            
            if metadata:
                print(f"✅ Found game metadata: type={metadata.get('game_type')}, series={metadata.get('series_description')}")
                return metadata
            else:
                print(f"⚠️ No metadata found for game {game_id}")
                return None
                
        except Exception as e:
            print(f"❌ Error fetching game metadata for {game_id}: {e}")
            return None

    def _load_boxscore_data(self, data, game_id=None):
        """Load boxscore JSON data."""
        try:
            # Use provided game_id or try to extract from data
            if game_id is None:
                game_id = self._extract_game_id_from_data(data)
            
            # If still no game_id, we can't proceed
            if game_id is None:
                print("❌ Could not extract game_id from data")
                return False
            
            queries = []
            
            # Save raw JSON
            queries.append(self._prepare_raw_json_query(game_id, 'boxscore', json.dumps(data)))
            
            # Extract game date
            game_date = None
            if 'gameDate' in data:
                game_date = data['gameDate'][:10]  # Extract date part
            elif 'liveData' in data and 'datetime' in data['liveData']:
                game_date = data['liveData']['datetime']['dateTime'][:10]
            
            # Fetch game metadata from schedule API for complete game info including game_type
            game_metadata = self._fetch_game_metadata_if_needed(game_id)
            
            # Process boxscore
            boxscore_queries = self._prepare_boxscore_data_queries(game_id, data, game_date)
            queries.extend(boxscore_queries)
            
            # If we have game metadata, also process the game record with proper metadata
            if game_metadata:
                # Create proper game data structure for _process_game_data with team information
                teams_data = data.get('teams', {})
                game_data_for_processing = {
                    'teams': teams_data,  # Include full team data from boxscore
                    'currentInning': data.get('liveData', {}).get('linescore', {}).get('currentInning'),
                    'inningState': data.get('liveData', {}).get('linescore', {}).get('inningState')
                }
                game_queries = self._prepare_game_data_queries(game_id, game_data_for_processing, game_date, game_metadata)
                queries.extend(game_queries)
            
            # Execute all queries in a transaction
            self.db.execute_transaction(queries)
            
            print(f"✅ Successfully loaded boxscore data for game {game_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error processing boxscore data: {e}")
            return False

    def _load_game_data(self, data):
        """Load game JSON data."""
        try:
            # Extract game_id from data
            game_id = self._extract_game_id_from_data(data)
            
            queries = []
            
            # Save raw JSON
            queries.append(self._prepare_raw_json_query(game_id, 'game_data', json.dumps(data)))
            
            # Process game data
            game_queries = self._prepare_game_data_queries(game_id, data, None, None)
            queries.extend(game_queries)
            
            # Execute all queries in a transaction
            self.db.execute_transaction(queries)
            
            print(f"✅ Successfully loaded game data for game {game_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error processing game data: {e}")
            return False

    def _prepare_raw_json_query(self, game_id, data_type, json_data):
        """Prepare raw JSON data query for transaction."""
        query = """
        INSERT INTO raw_json_data (game_id, data_type, json_data, extraction_timestamp)
        VALUES (?, ?, ?, ?)
        """
        params = (game_id, data_type, json_data, datetime.now())
        return (query, params)

    def _prepare_game_data_queries(self, game_id, game_data, game_date=None, game_metadata=None):
        """Prepare game data queries for transaction."""
        queries = []
        
        try:
            # Extract teams info
            teams_data = game_data.get('teams', {})
            home_team = teams_data.get('home', {}).get('team', {})
            away_team = teams_data.get('away', {}).get('team', {})
            
            # Prepare team insert queries if they don't exist
            if home_team:
                queries.append(self._prepare_team_query(home_team))
            if away_team:
                queries.append(self._prepare_team_query(away_team))
            
            # Prepare game insert/update query
            queries.append(self._prepare_game_query(game_id, game_data, home_team, away_team, game_date, game_metadata))
            
            return queries
            
        except Exception as e:
            print(f"❌ Error preparing game data queries: {e}")
            raise

    def _prepare_boxscore_data_queries(self, game_id, boxscore_data, game_date=None):
        """Prepare boxscore data queries for transaction."""
        queries = []
        
        try:
            teams = boxscore_data.get('teams', {})
            
            for team_type in ['home', 'away']:
                team_data = teams.get(team_type, {})
                team_info = team_data.get('team', {})
                players = team_data.get('players', {})
                
                # Prepare team query
                if team_info:
                    queries.append(self._prepare_team_query(team_info))
                
                # Prepare player and batting stats queries
                for player_key, player_data in players.items():
                    if player_key.startswith('ID'):
                        person = player_data.get('person', {})
                        stats = player_data.get('stats', {})
                        
                        # Prepare player query
                        if person:
                            queries.append(self._prepare_player_query(person, team_info.get('id')))
                        
                        # Prepare batting stats query
                        batting = stats.get('batting', {})
                        if batting:
                            queries.append(self._prepare_boxscore_stats_query(game_id, person.get('id'), 
                                                                            team_info.get('id'), batting, game_date))
            
            return queries
            
        except Exception as e:
            print(f"❌ Error preparing boxscore data queries: {e}")
            raise

    def _prepare_team_query(self, team_data):
        """Prepare team insert query."""
        query = """
        IF NOT EXISTS (SELECT 1 FROM teams WHERE team_id = ?)
        INSERT INTO teams (team_id, team_name, abbreviation, league, division)
        VALUES (?, ?, ?, ?, ?)
        """
        params = (
            team_data.get('id'),  # For EXISTS check
            team_data.get('id'),
            team_data.get('name'),
            team_data.get('abbreviation'),
            team_data.get('league', {}).get('name'),
            team_data.get('division', {}).get('name')
        )
        return (query, params)

    def _prepare_player_query(self, player_data, team_id):
        """Prepare player insert query."""
        query = """
        IF NOT EXISTS (SELECT 1 FROM players WHERE player_id = ?)
        INSERT INTO players (player_id, player_name, team_id, position)
        VALUES (?, ?, ?, ?)
        """
        params = (
            player_data.get('id'),  # For EXISTS check
            player_data.get('id'),
            player_data.get('fullName'),
            team_id,
            player_data.get('primaryPosition', {}).get('name')
        )
        return (query, params)

    def _prepare_game_query(self, game_id, game_data, home_team, away_team, game_date=None, game_metadata=None):
        """Prepare game insert/update query."""
        teams_data = game_data.get('teams', {})
        home_score = teams_data.get('home', {}).get('runs', 0)
        away_score = teams_data.get('away', {}).get('runs', 0)
        
        # Initialize metadata with defaults
        if game_metadata is None:
            game_metadata = {}
        
        # Parse the game date properly
        if game_date:
            # Use the provided game_date from combined data
            if isinstance(game_date, str):
                parsed_date = datetime.strptime(game_date, '%Y-%m-%d').date()
            else:
                parsed_date = game_date
        else:
            # Fallback to extracting from game data or current date
            game_datetime = game_data.get('gameDate')
            if game_datetime:
                try:
                    parsed_date = datetime.fromisoformat(game_datetime.replace('Z', '+00:00')).date()
                except:
                    parsed_date = datetime.now().date()
            else:
                parsed_date = datetime.now().date()
        
        query = """
        IF NOT EXISTS (SELECT 1 FROM games WHERE game_id = ?)
        INSERT INTO games (game_id, game_date, home_team_id, away_team_id, 
                          home_score, away_score, inning, inning_state, game_status,
                          game_type, series_description, official_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ELSE
        UPDATE games SET 
            game_date = ?,
            home_team_id = ?,
            away_team_id = ?,
            home_score = ?,
            away_score = ?,
            inning = ?,
            inning_state = ?,
            game_status = ?,
            game_type = ?,
            series_description = ?,
            official_date = ?
        WHERE game_id = ?
        """
        params = (
            game_id,  # For EXISTS check
            game_id,
            parsed_date,
            home_team.get('id'),
            away_team.get('id'),
            home_score,
            away_score,
            game_data.get('currentInning'),
            game_data.get('inningState'),
            'Live' if game_data.get('currentInning') else 'Final',
            game_metadata.get('game_type') or game_data.get('gameType'),
            game_metadata.get('series_description') or game_data.get('seriesDescription'),
            game_metadata.get('official_date') or game_data.get('officialDate'),
            # Update parameters
            parsed_date,
            home_team.get('id'),
            away_team.get('id'),
            home_score,
            away_score,
            game_data.get('currentInning'),
            game_data.get('inningState'),
            'Live' if game_data.get('currentInning') else 'Final',
            game_metadata.get('game_type') or game_data.get('gameType'),
            game_metadata.get('series_description') or game_data.get('seriesDescription'),
            game_metadata.get('official_date') or game_data.get('officialDate'),
            game_id  # For WHERE clause
        )
        return (query, params)

    def _prepare_boxscore_stats_query(self, game_id, player_id, team_id, batting_stats, game_date=None):
        """Prepare boxscore batting statistics query."""
        query = """
        IF NOT EXISTS (SELECT 1 FROM boxscore WHERE game_id = ? AND player_id = ?)
        INSERT INTO boxscore (game_id, player_id, team_id, at_bats, runs, hits, doubles, triples, home_runs, rbi, walks, strikeouts, stolen_bases, caught_stealing, game_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            game_id, player_id,  # For EXISTS check
            game_id,
            player_id,
            team_id,
            batting_stats.get('atBats', 0),
            batting_stats.get('runs', 0),
            batting_stats.get('hits', 0),
            batting_stats.get('doubles', 0),
            batting_stats.get('triples', 0),
            batting_stats.get('homeRuns', 0),
            batting_stats.get('rbi', 0),
            batting_stats.get('baseOnBalls', 0),  # Fixed: baseOnBalls is the correct JSON field
            batting_stats.get('strikeOuts', 0),
            batting_stats.get('stolenBases', 0),  # New: capture stolen bases
            batting_stats.get('caughtStealing', 0),  # New: capture caught stealing
            game_date
        )
        return (query, params)

    def _extract_game_id_from_data(self, data):
        """Extract game ID from various data structures."""
        # Try different ways to find game_id
        if isinstance(data, dict):
            if 'game_id' in data:
                return data['game_id']
            if 'gamePk' in data:
                return data['gamePk']
            # Look in nested structures
            for key, value in data.items():
                if isinstance(value, dict) and 'gamePk' in value:
                    return value['gamePk']
        
        # If no game_id found in data, try to get it from current context
        # This is a fallback - ideally the caller should pass the game_id explicitly
        if hasattr(self, '_current_game_id'):
            return self._current_game_id
            
        return None

    def load_schedule_data(self, schedule_data):
        """
        Load games from MLB schedule API data into the games table.
        
        Args:
            schedule_data: JSON data from MLB schedule API
        """
        try:
            if not self.db.connect():
                print("❌ Failed to connect to Fabric")
                return False
            
            total_games = 0
            success_count = 0
            queries = []
            
            # Process each date in the schedule
            for date_entry in schedule_data.get('dates', []):
                game_date = date_entry.get('date')
                games = date_entry.get('games', [])
                
                print(f"📅 Processing {len(games)} games for {game_date}")
                
                for game in games:
                    try:
                        total_games += 1
                        game_query = self._prepare_scheduled_game_query(game, game_date)
                        if game_query:
                            queries.append(game_query)
                            
                            # Extract teams and add team queries
                            home_team = game.get('teams', {}).get('home', {}).get('team', {})
                            away_team = game.get('teams', {}).get('away', {}).get('team', {})
                            
                            if home_team:
                                queries.append(self._prepare_team_query(home_team))
                            if away_team:
                                queries.append(self._prepare_team_query(away_team))
                            
                            success_count += 1
                    except Exception as e:
                        print(f"❌ Error processing game {game.get('gamePk', 'Unknown')}: {e}")
            
            # Execute all queries in a transaction
            if queries:
                self.db.execute_transaction(queries)
            
            print(f"✅ Successfully loaded {success_count}/{total_games} scheduled games")
            return success_count == total_games
            
        except Exception as e:
            print(f"❌ Error loading schedule data: {e}")
            return False
        finally:
            self.db.disconnect()

    def _prepare_scheduled_game_query(self, game_data, game_date):
        """Prepare a scheduled game query for transaction."""
        try:
            game_id = game_data.get('gamePk')
            if not game_id:
                return None
            
            # Extract team information
            teams = game_data.get('teams', {})
            home_team = teams.get('home', {}).get('team', {})
            away_team = teams.get('away', {}).get('team', {})
            
            # Extract game status and score information
            status = game_data.get('status', {})
            game_status = status.get('detailedState', 'Scheduled')
            
            # Extract scores from linescore if available
            linescore = game_data.get('linescore', {})
            home_score = 0
            away_score = 0
            current_inning = None
            inning_state = None
            
            if linescore:
                home_score = linescore.get('teams', {}).get('home', {}).get('runs', 0)
                away_score = linescore.get('teams', {}).get('away', {}).get('runs', 0)
                current_inning = linescore.get('currentInning')
                inning_state = linescore.get('inningState')
            
            # Extract game date and time
            game_datetime = game_data.get('gameDate')
            if game_datetime:
                # Parse ISO datetime string
                parsed_date = datetime.fromisoformat(game_datetime.replace('Z', '+00:00')).date()
            else:
                # Fallback to date from schedule
                parsed_date = datetime.strptime(game_date, '%Y-%m-%d').date()
            
            # Extract game type and series information
            game_type = game_data.get('gameType', None)
            series_description = game_data.get('seriesDescription', None)
            official_date = game_data.get('officialDate', None)
            
            # Parse official date if available
            if official_date:
                try:
                    official_date_parsed = datetime.strptime(official_date, '%Y-%m-%d').date()
                except:
                    official_date_parsed = None
            else:
                official_date_parsed = None
            
            # Prepare the game query
            query = """
            IF NOT EXISTS (SELECT 1 FROM games WHERE game_id = ?)
            INSERT INTO games (game_id, game_date, home_team_id, away_team_id, 
                              home_score, away_score, inning, inning_state, game_status,
                              game_type, series_description, official_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ELSE
            UPDATE games SET 
                game_date = ?,
                home_team_id = ?,
                away_team_id = ?,
                home_score = ?,
                away_score = ?,
                inning = ?,
                inning_state = ?,
                game_status = ?,
                game_type = ?,
                series_description = ?,
                official_date = ?
            WHERE game_id = ?
            """
            
            params = (
                game_id,  # For EXISTS check
                game_id,
                parsed_date,
                home_team.get('id'),
                away_team.get('id'),
                home_score,
                away_score,
                current_inning,
                inning_state,
                game_status,
                game_type,
                series_description,
                official_date_parsed,
                # Update parameters
                parsed_date,
                home_team.get('id'),
                away_team.get('id'),
                home_score,
                away_score,
                current_inning,
                inning_state,
                game_status,
                game_type,
                series_description,
                official_date_parsed,
                game_id  # For WHERE clause
            )
            
            return (query, params)
            
        except Exception as e:
            print(f"❌ Error preparing scheduled game query: {e}")
            return None

    def load_directory(self, json_directory):
        """Load all JSON files from the specified directory."""
        json_dir = Path(json_directory)
        if not json_dir.exists():
            print(f"❌ Directory not found: {json_directory}")
            return False

        json_files = list(json_dir.glob("*.json"))
        if not json_files:
            print(f"❌ No JSON files found in {json_directory}")
            return False

        print(f"📁 Found {len(json_files)} JSON files to process")
        
        # Create database tables if they don't exist
        fabric_db = FabricConnection()
        if fabric_db.connect():
            fabric_db.create_tables()
            fabric_db.disconnect()
        
        # Process each JSON file
        total_files = len(json_files)
        success_count = 0
        
        for json_file in json_files:
            print(f"📄 Processing {json_file.name}...")
            if self.load_json_to_database(json_file):
                success_count += 1
            else:
                print(f"❌ Failed to load {json_file.name}")
        
        print(f"✅ Successfully loaded {success_count}/{total_files} JSON files")
        return success_count == total_files

    def clear_existing_data(self, game_ids=None):
        """
        Clear existing data from tables.
        
        Args:
            game_ids: List of specific game IDs to clear. If None, clears all data.
        """
        try:
            if not self.db.connect():
                print("❌ Failed to connect to Fabric")
                return False
            
            if game_ids:
                # Clear specific games
                print(f"🧹 Clearing data for {len(game_ids)} specific games...")
                game_ids_str = ','.join(map(str, game_ids))
                
                queries = [
                    f"DELETE FROM boxscore WHERE game_id IN ({game_ids_str})",
                    f"DELETE FROM raw_json_data WHERE game_id IN ({game_ids_str})",
                    f"DELETE FROM games WHERE game_id IN ({game_ids_str})"
                ]
            else:
                # Clear all data
                print("🧹 Clearing all data from tables...")
                queries = [
                    "DELETE FROM boxscore",
                    "DELETE FROM raw_json_data", 
                    "DELETE FROM games",
                    "DELETE FROM players",
                    "DELETE FROM teams"
                ]
            
            # Execute deletion queries in transaction
            self.db.execute_transaction(queries)
            print("✅ Data cleared successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error clearing data: {e}")
            return False
        finally:
            self.db.disconnect()
