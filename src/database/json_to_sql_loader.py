import json
import os
from datetime import datetime
from pathlib import Path
from src.database.connection import DatabaseConnection
from src.utils.json_handler import load_from_json

class JSONToSQLLoader:
    def __init__(self, db_connection=None):
        """
        Initialize the JSON to SQL loader.
        
        Args:
            db_connection: DatabaseConnection instance (optional)
        """
        self.db = db_connection or DatabaseConnection()

    def load_json_to_database(self, json_file_path):
        """
        Load data from a JSON file into the SQL Server database.
        
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
                print("❌ Failed to connect to database")
                return False

            # Determine the type of JSON file and process accordingly
            if 'combined_data' in str(json_file_path):
                return self._load_combined_data(data)
            elif 'boxscore_raw' in str(json_file_path):
                return self._load_boxscore_data(data)
            elif 'game_raw' in str(json_file_path):
                return self._load_game_data(data)
            else:
                print(f"❌ Unknown JSON file type: {json_file_path}")
                return False

        except Exception as e:
            print(f"❌ Error loading JSON to database: {e}")
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
            with self.db.connection.begin() as trans:
                # First, save raw JSON data for backup
                self._save_raw_json(game_id, 'combined', json.dumps(data))
                
                # Extract and load game data with proper date and metadata
                if 'game_data' in data:
                    self._process_game_data(game_id, data['game_data'], game_date, game_metadata)
                
                # Extract and load boxscore data
                if 'boxscore' in data:
                    self._process_boxscore_data(game_id, data['boxscore'])
                
                # Transaction will be committed automatically when exiting the context
            
            print(f"✅ Successfully loaded combined data for game {game_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error processing combined data: {e}")
            # Transaction will be rolled back automatically on exception
            return False

    def _load_boxscore_data(self, data):
        """Load boxscore JSON data."""
        try:
            # Extract game_id from filename or data
            game_id = self._extract_game_id_from_data(data)
            
            # Save raw JSON
            self._save_raw_json(game_id, 'boxscore', json.dumps(data))
            
            # Process boxscore
            self._process_boxscore_data(game_id, data)
            
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
            
            # Save raw JSON
            self._save_raw_json(game_id, 'game_data', json.dumps(data))
            
            # Process game data
            self._process_game_data(game_id, data, None, None)
            
            print(f"✅ Successfully loaded game data for game {game_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error processing game data: {e}")
            return False

    def _save_raw_json(self, game_id, data_type, json_data):
        """Save raw JSON data to the database."""
        query = """
        INSERT INTO raw_json_data (game_id, data_type, json_data, extraction_timestamp)
        VALUES (:game_id, :data_type, :json_data, :timestamp)
        """
        params = {
            'game_id': game_id,
            'data_type': data_type,
            'json_data': json_data,
            'timestamp': datetime.now()
        }
        self.db.execute_query(query, params)

    def _process_game_data(self, game_id, game_data, game_date=None, game_metadata=None):
        """Process and insert game data."""
        try:
            # Extract teams info
            teams_data = game_data.get('teams', {})
            home_team = teams_data.get('home', {}).get('team', {})
            away_team = teams_data.get('away', {}).get('team', {})
            
            # Insert teams if they don't exist
            if home_team:
                self._insert_team(home_team)
            if away_team:
                self._insert_team(away_team)
            
            # Insert/update game with proper date and metadata
            self._insert_game(game_id, game_data, home_team, away_team, game_date, game_metadata)
            
        except Exception as e:
            print(f"❌ Error processing game data: {e}")
            raise

    def _process_boxscore_data(self, game_id, boxscore_data):
        """Process and insert boxscore data."""
        try:
            teams = boxscore_data.get('teams', {})
            
            for team_type in ['home', 'away']:
                team_data = teams.get(team_type, {})
                team_info = team_data.get('team', {})
                players = team_data.get('players', {})
                
                # Insert team
                if team_info:
                    self._insert_team(team_info)
                
                # Insert players and their stats
                for player_key, player_data in players.items():
                    if player_key.startswith('ID'):
                        person = player_data.get('person', {})
                        stats = player_data.get('stats', {})
                        
                        # Insert player
                        if person:
                            self._insert_player(person, team_info.get('id'))
                        
                        # Insert batting stats
                        batting = stats.get('batting', {})
                        if batting:
                            self._insert_boxscore_stats(game_id, person.get('id'), 
                                                      team_info.get('id'), batting)
            
        except Exception as e:
            print(f"❌ Error processing boxscore data: {e}")
            raise

    def _insert_team(self, team_data):
        """Insert or update team data."""
        query = """
        IF NOT EXISTS (SELECT 1 FROM teams WHERE team_id = :team_id)
        INSERT INTO teams (team_id, team_name, abbreviation, league, division)
        VALUES (:team_id, :team_name, :abbreviation, :league, :division)
        """
        params = {
            'team_id': team_data.get('id'),
            'team_name': team_data.get('name'),
            'abbreviation': team_data.get('abbreviation'),
            'league': team_data.get('league', {}).get('name'),
            'division': team_data.get('division', {}).get('name')
        }
        self.db.execute_query(query, params)

    def _insert_player(self, player_data, team_id):
        """Insert or update player data."""
        query = """
        IF NOT EXISTS (SELECT 1 FROM players WHERE player_id = :player_id)
        INSERT INTO players (player_id, player_name, team_id, position)
        VALUES (:player_id, :player_name, :team_id, :position)
        """
        params = {
            'player_id': player_data.get('id'),
            'player_name': player_data.get('fullName'),
            'team_id': team_id,
            'position': player_data.get('primaryPosition', {}).get('name')
        }
        self.db.execute_query(query, params)

    def _insert_game(self, game_id, game_data, home_team, away_team, game_date=None, game_metadata=None):
        """Insert or update game data."""
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
        IF NOT EXISTS (SELECT 1 FROM games WHERE game_id = :game_id)
        INSERT INTO games (game_id, game_date, home_team_id, away_team_id, 
                          home_score, away_score, inning, inning_state, game_status,
                          game_type, series_description, official_date)
        VALUES (:game_id, :game_date, :home_team_id, :away_team_id, 
                :home_score, :away_score, :inning, :inning_state, :game_status,
                :game_type, :series_description, :official_date)
        ELSE
        UPDATE games SET 
            game_date = :game_date,
            home_score = :home_score,
            away_score = :away_score,
            inning = :inning,
            inning_state = :inning_state,
            game_status = :game_status,
            game_type = :game_type,
            series_description = :series_description,
            official_date = :official_date
        WHERE game_id = :game_id
        """
        params = {
            'game_id': game_id,
            'game_date': parsed_date,  # Use the properly parsed date
            'home_team_id': home_team.get('id'),
            'away_team_id': away_team.get('id'),
            'home_score': home_score,
            'away_score': away_score,
            'inning': game_data.get('currentInning'),
            'inning_state': game_data.get('inningState'),
            'game_status': 'Live' if game_data.get('currentInning') else 'Final',
            'game_type': game_metadata.get('game_type') or game_data.get('gameType'),  # Use metadata first, fallback to game_data
            'series_description': game_metadata.get('series_description') or game_data.get('seriesDescription'),  # Use metadata first
            'official_date': game_metadata.get('official_date') or game_data.get('officialDate')  # Use metadata first
        }
        self.db.execute_query(query, params)

    def _insert_boxscore_stats(self, game_id, player_id, team_id, batting_stats):
        """Insert boxscore batting statistics."""
        query = """
        IF NOT EXISTS (SELECT 1 FROM boxscore WHERE game_id = :game_id AND player_id = :player_id)
        INSERT INTO boxscore (game_id, player_id, team_id, at_bats, runs, hits, doubles, triples, home_runs, rbi, walks, strikeouts)
        VALUES (:game_id, :player_id, :team_id, :at_bats, :runs, :hits, :doubles, :triples, :home_runs, :rbi, :walks, :strikeouts)
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
            'walks': batting_stats.get('walks', 0),
            'strikeouts': batting_stats.get('strikeOuts', 0)
        }
        self.db.execute_query(query, params)

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
        return None

    def load_schedule_data(self, schedule_data):
        """
        Load games from MLB schedule API data into the games table.
        
        Args:
            schedule_data: JSON data from MLB schedule API
        """
        try:
            if not self.db.connect():
                print("❌ Failed to connect to database")
                return False
            
            total_games = 0
            success_count = 0
            
            # Process each date in the schedule
            for date_entry in schedule_data.get('dates', []):
                game_date = date_entry.get('date')
                games = date_entry.get('games', [])
                
                print(f"📅 Processing {len(games)} games for {game_date}")
                
                for game in games:
                    try:
                        total_games += 1
                        if self._insert_scheduled_game(game, game_date):
                            success_count += 1
                    except Exception as e:
                        print(f"❌ Error processing game {game.get('gamePk', 'Unknown')}: {e}")
            
            print(f"✅ Successfully loaded {success_count}/{total_games} scheduled games")
            return success_count == total_games
            
        except Exception as e:
            print(f"❌ Error loading schedule data: {e}")
            return False
        finally:
            self.db.disconnect()

    def _insert_scheduled_game(self, game_data, game_date):
        """Insert or update a scheduled game from schedule API."""
        try:
            game_id = game_data.get('gamePk')
            if not game_id:
                return False
            
            # Extract team information
            teams = game_data.get('teams', {})
            home_team = teams.get('home', {}).get('team', {})
            away_team = teams.get('away', {}).get('team', {})
            
            # Insert teams if they don't exist
            if home_team:
                self._insert_team(home_team)
            if away_team:
                self._insert_team(away_team)
            
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
                from datetime import datetime
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
                    from datetime import datetime
                    official_date_parsed = datetime.strptime(official_date, '%Y-%m-%d').date()
                except:
                    official_date_parsed = None
            else:
                official_date_parsed = None
            
            # Insert or update the game
            query = """
            IF NOT EXISTS (SELECT 1 FROM games WHERE game_id = :game_id)
            INSERT INTO games (game_id, game_date, home_team_id, away_team_id, 
                              home_score, away_score, inning, inning_state, game_status,
                              game_type, series_description, official_date)
            VALUES (:game_id, :game_date, :home_team_id, :away_team_id, 
                    :home_score, :away_score, :inning, :inning_state, :game_status,
                    :game_type, :series_description, :official_date)
            ELSE
            UPDATE games SET 
                game_date = :game_date,
                home_team_id = :home_team_id,
                away_team_id = :away_team_id,
                home_score = :home_score,
                away_score = :away_score,
                inning = :inning,
                inning_state = :inning_state,
                game_status = :game_status,
                game_type = :game_type,
                series_description = :series_description,
                official_date = :official_date
            WHERE game_id = :game_id
            """
            
            params = {
                'game_id': game_id,
                'game_date': parsed_date,
                'home_team_id': home_team.get('id'),
                'away_team_id': away_team.get('id'),
                'home_score': home_score,
                'away_score': away_score,
                'inning': current_inning,
                'inning_state': inning_state,
                'game_status': game_status,
                'game_type': game_type,
                'series_description': series_description,
                'official_date': official_date_parsed
            }
            
            self.db.execute_query(query, params)
            return True
            
        except Exception as e:
            print(f"❌ Error inserting scheduled game: {e}")
            return False
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
        db = DatabaseConnection()
        if db.connect():
            db.create_tables()
            db.disconnect()
            
    def load_schedule_data(self, schedule_data):
        """
        Load schedule data directly from MLB API response into the games table.
        This populates games with proper metadata including game_type.
        
        Args:
            schedule_data: Schedule data from MLB API
            
        Returns:
            bool: Success status
        """
        try:
            if not self.db.connect():
                print("❌ Failed to connect to database")
                return False
                
            games_loaded = 0
            
            # Process each date in the schedule
            for date_entry in schedule_data.get('dates', []):
                game_date = date_entry.get('date')
                games = date_entry.get('games', [])
                
                print(f"📅 Processing {len(games)} games for {game_date}")
                
                for game in games:
                    try:
                        # Extract game information
                        game_id = game.get('gamePk')
                        home_team = game.get('teams', {}).get('home', {}).get('team', {})
                        away_team = game.get('teams', {}).get('away', {}).get('team', {})
                        
                        # Insert teams if they don't exist
                        if home_team:
                            self._insert_team(home_team)
                        if away_team:
                            self._insert_team(away_team)
                        
                        # Insert/update game with schedule metadata
                        self._insert_game_from_schedule(game_id, game, game_date)
                        games_loaded += 1
                        
                    except Exception as e:
                        print(f"❌ Error processing game {game.get('gamePk')}: {e}")
                        continue
            
            print(f"✅ Successfully loaded {games_loaded} games from schedule")
            return True
            
        except Exception as e:
            print(f"❌ Error loading schedule data: {e}")
            return False
        finally:
            self.db.disconnect()
    
    def _insert_game_from_schedule(self, game_id, game_data, game_date):
        """Insert or update game data from schedule API."""
        # Parse game date
        if isinstance(game_date, str):
            parsed_date = datetime.strptime(game_date, '%Y-%m-%d').date()
        else:
            parsed_date = game_date
            
        # Extract team information
        teams_data = game_data.get('teams', {})
        home_team = teams_data.get('home', {}).get('team', {})
        away_team = teams_data.get('away', {}).get('team', {})
        
        # Extract scores from linescore if available
        linescore = game_data.get('linescore', {})
        home_score = linescore.get('teams', {}).get('home', {}).get('runs', 0)
        away_score = linescore.get('teams', {}).get('away', {}).get('runs', 0)
        
        # Extract game status
        status = game_data.get('status', {})
        game_status = status.get('detailedState', status.get('abstractGameState', 'Unknown'))
        
        query = """
        IF NOT EXISTS (SELECT 1 FROM games WHERE game_id = :game_id)
        INSERT INTO games (game_id, game_date, home_team_id, away_team_id, 
                          home_score, away_score, inning, inning_state, game_status,
                          game_type, series_description, official_date)
        VALUES (:game_id, :game_date, :home_team_id, :away_team_id, 
                :home_score, :away_score, :inning, :inning_state, :game_status,
                :game_type, :series_description, :official_date)
        ELSE
        UPDATE games SET 
            game_date = :game_date,
            home_score = :home_score,
            away_score = :away_score,
            inning = :inning,
            inning_state = :inning_state,
            game_status = :game_status,
            game_type = :game_type,
            series_description = :series_description,
            official_date = :official_date
        WHERE game_id = :game_id
        """
        
        params = {
            'game_id': game_id,
            'game_date': parsed_date,
            'home_team_id': home_team.get('id'),
            'away_team_id': away_team.get('id'),
            'home_score': home_score,
            'away_score': away_score,
            'inning': linescore.get('currentInning'),
            'inning_state': linescore.get('inningState'),
            'game_status': game_status,
            'game_type': game_data.get('gameType'),  # This is the key field we wanted!
            'series_description': game_data.get('seriesDescription'),
            'official_date': game_data.get('officialDate')
        }
        
        self.db.execute_query(query, params)
