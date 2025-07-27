#!/usr/bin/env python3
"""
Game Type Analysis Utility
Provides functions to filter and analyze games by type (regular season vs preseason/spring training).
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database.connection import DatabaseConnection

class GameTypeAnalyzer:
    def __init__(self):
        self.db = DatabaseConnection()
        
        # Game type mappings
        self.game_types = {
            'S': 'Spring Training / Preseason',
            'R': 'Regular Season',
            'F': 'Wild Card / First Round',
            'D': 'Division Series', 
            'L': 'League Championship Series',
            'W': 'World Series',
            'A': 'All-Star Game'
        }
    
    def get_games_by_type(self, game_type=None, limit=None):
        """
        Get games filtered by game type.
        
        Args:
            game_type: Game type code ('S', 'R', 'F', 'D', 'L', 'W', 'A') or None for all
            limit: Maximum number of games to return
        
        Returns:
            List of game records
        """
        try:
            self.db.connect()
            
            base_query = """
            SELECT g.game_id, g.game_date, g.official_date, g.game_type, g.series_description,
                   g.game_status, g.home_score, g.away_score,
                   ht.team_name as home_team, at.team_name as away_team
            FROM games g
            LEFT JOIN teams ht ON g.home_team_id = ht.team_id
            LEFT JOIN teams at ON g.away_team_id = at.team_id
            """
            
            if game_type:
                query = base_query + " WHERE g.game_type = :game_type"
                params = {'game_type': game_type}
            else:
                query = base_query
                params = {}
            
            query += " ORDER BY g.game_date DESC"
            
            if limit:
                query += f" OFFSET 0 ROWS FETCH NEXT {limit} ROWS ONLY"
            
            results = self.db.fetch_results(query, params)
            return results
            
        except Exception as e:
            print(f"❌ Error fetching games: {e}")
            return []
    
    def get_game_type_summary(self):
        """Get a summary of games by type."""
        try:
            self.db.connect()
            
            query = """
            SELECT game_type, series_description, COUNT(*) as game_count,
                   MIN(game_date) as earliest_date, MAX(game_date) as latest_date
            FROM games 
            WHERE game_type IS NOT NULL
            GROUP BY game_type, series_description
            ORDER BY game_type, series_description
            """
            
            results = self.db.fetch_results(query)
            return results
            
        except Exception as e:
            print(f"❌ Error fetching summary: {e}")
            return []
    
    def is_preseason_game(self, game_id):
        """
        Check if a specific game is a preseason/spring training game.
        
        Args:
            game_id: The game ID to check
            
        Returns:
            True if preseason, False if regular season, None if not found
        """
        try:
            self.db.connect()
            
            query = "SELECT game_type FROM games WHERE game_id = :game_id"
            results = self.db.fetch_results(query, {'game_id': game_id})
            
            if results:
                game_type = results[0][0]
                return game_type == 'S'  # 'S' = Spring Training
            return None
            
        except Exception as e:
            print(f"❌ Error checking game type: {e}")
            return None
    
    def get_spring_training_games(self, year=None, limit=50):
        """Get spring training games, optionally filtered by year."""
        try:
            self.db.connect()
            
            query = """
            SELECT g.game_id, g.game_date, g.official_date, g.series_description,
                   g.game_status, g.home_score, g.away_score,
                   ht.team_name as home_team, at.team_name as away_team
            FROM games g
            LEFT JOIN teams ht ON g.home_team_id = ht.team_id
            LEFT JOIN teams at ON g.away_team_id = at.team_id
            WHERE g.game_type = 'S'
            """
            
            params = {}
            if year:
                query += " AND YEAR(g.game_date) = :year"
                params['year'] = year
            
            query += " ORDER BY g.game_date DESC"
            
            if limit:
                query += f" OFFSET 0 ROWS FETCH NEXT {limit} ROWS ONLY"
            
            results = self.db.fetch_results(query, params)
            return results
            
        except Exception as e:
            print(f"❌ Error fetching spring training games: {e}")
            return []
    
    def get_regular_season_games(self, year=None, limit=50):
        """Get regular season games, optionally filtered by year."""
        try:
            self.db.connect()
            
            query = """
            SELECT g.game_id, g.game_date, g.official_date, g.series_description,
                   g.game_status, g.home_score, g.away_score,
                   ht.team_name as home_team, at.team_name as away_team
            FROM games g
            LEFT JOIN teams ht ON g.home_team_id = ht.team_id
            LEFT JOIN teams at ON g.away_team_id = at.team_id
            WHERE g.game_type = 'R'
            """
            
            params = {}
            if year:
                query += " AND YEAR(g.game_date) = :year"
                params['year'] = year
            
            query += " ORDER BY g.game_date DESC"
            
            if limit:
                query += f" OFFSET 0 ROWS FETCH NEXT {limit} ROWS ONLY"
            
            results = self.db.fetch_results(query, params)
            return results
            
        except Exception as e:
            print(f"❌ Error fetching regular season games: {e}")
            return []
    
    def print_game_type_summary(self):
        """Print a formatted summary of games by type."""
        summary = self.get_game_type_summary()
        
        print("\n📊 GAME TYPE SUMMARY")
        print("=" * 80)
        print(f"{'Type':<6} {'Description':<25} {'Count':<8} {'Date Range':<20}")
        print("-" * 80)
        
        for row in summary:
            game_type = row[0] or 'NULL'
            series_desc = row[1] or 'Unknown'
            count = row[2]
            earliest = row[3].strftime('%Y-%m-%d') if row[3] else 'N/A'
            latest = row[4].strftime('%Y-%m-%d') if row[4] else 'N/A'
            date_range = f"{earliest} to {latest}"
            
            type_desc = self.game_types.get(game_type, 'Unknown Type')
            print(f"{game_type:<6} {series_desc:<25} {count:<8} {date_range:<20}")
        
        print("\n🏷️  GAME TYPE CODES:")
        for code, description in self.game_types.items():
            print(f"   {code} = {description}")
    
    def update_existing_game_types(self, start_date, end_date):
        """
        Update game type information for existing games by fetching from schedule API.
        This is useful for backfilling game type data.
        """
        try:
            from api.mlb_client import MLBClient
            from database.json_to_sql_loader import JsonToSqlLoader
            
            client = MLBClient()
            loader = JsonToSqlLoader()
            
            print(f"Fetching schedule data from {start_date} to {end_date}...")
            schedule_data = client.fetch_schedule(start_date, end_date)
            
            print("Updating game type information...")
            success = loader.load_schedule_data(schedule_data)
            
            if success:
                print("✅ Game type information updated successfully!")
            else:
                print("❌ Failed to update game type information")
                
            return success
            
        except Exception as e:
            print(f"❌ Error updating game types: {e}")
            return False
    
    def __del__(self):
        if hasattr(self, 'db'):
            self.db.disconnect()

def main():
    """Demo the game type analyzer."""
    analyzer = GameTypeAnalyzer()
    
    # Show summary
    analyzer.print_game_type_summary()
    
    # Show some spring training games
    print(f"\n🌸 RECENT SPRING TRAINING GAMES:")
    print("-" * 80)
    spring_games = analyzer.get_spring_training_games(limit=10)
    
    for game in spring_games:
        game_id, game_date, official_date, series_desc, status, home_score, away_score, home_team, away_team = game
        date_str = game_date.strftime('%Y-%m-%d') if game_date else 'N/A'
        print(f"Game {game_id}: {away_team} @ {home_team} ({date_str}) - {status}")
    
    # Show some regular season games
    print(f"\n⚾ RECENT REGULAR SEASON GAMES:")
    print("-" * 80)
    regular_games = analyzer.get_regular_season_games(limit=5)
    
    if regular_games:
        for game in regular_games:
            game_id, game_date, official_date, series_desc, status, home_score, away_score, home_team, away_team = game
            date_str = game_date.strftime('%Y-%m-%d') if game_date else 'N/A'
            print(f"Game {game_id}: {away_team} @ {home_team} ({date_str}) - {status}")
    else:
        print("No regular season games found in database")

if __name__ == "__main__":
    main()
