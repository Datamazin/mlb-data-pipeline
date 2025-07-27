#!/usr/bin/env python3
"""
View MLB Database Data
This script displays the data that has been loaded into your SQL Server database.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import pyodbc
from sqlalchemy import create_engine, text

def view_database_data():
    """Display the data in the MLB database."""
    try:
        # Connect to database
        connection_string = (
            "mssql+pyodbc://localhost/mlb_data?"
            "driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
        )
        engine = create_engine(connection_string)
        conn = engine.connect()
        
        print("MLB Database Contents")
        print("=" * 60)
        
        # Teams
        print("\n📊 TEAMS:")
        teams = conn.execute(text("SELECT team_id, team_name, abbreviation, league FROM teams")).fetchall()
        for team in teams:
            print(f"  {team[0]:>3} | {team[1]:<25} | {team[2]:<4} | {team[3]}")
        
        # Games
        print(f"\n🏟️  GAMES:")
        games = conn.execute(text("""
            SELECT g.game_id, g.game_date, 
                   ht.team_name as home_team, g.home_score,
                   at.team_name as away_team, g.away_score,
                   g.inning, g.inning_state, g.game_status
            FROM games g
            LEFT JOIN teams ht ON g.home_team_id = ht.team_id  
            LEFT JOIN teams at ON g.away_team_id = at.team_id
            ORDER BY g.game_date DESC
        """)).fetchall()
        
        for game in games:
            print(f"  Game {game[0]} | {game[1]} | {game[2] or 'TBD'} {game[3]} - {game[5]} {game[4] or 'TBD'}")
            print(f"    Inning: {game[6]} {game[7]} | Status: {game[8]}")
        
        # Top Players by Stats
        print(f"\n⚾ TOP PLAYERS BY HITS:")
        top_players = conn.execute(text("""
            SELECT TOP 10 p.player_name, t.team_name, 
                   SUM(b.hits) as total_hits, 
                   SUM(b.runs) as total_runs,
                   SUM(b.rbi) as total_rbi
            FROM boxscore b
            JOIN players p ON b.player_id = p.player_id
            JOIN teams t ON b.team_id = t.team_id
            GROUP BY p.player_name, t.team_name
            HAVING SUM(b.hits) > 0
            ORDER BY total_hits DESC, total_runs DESC
        """)).fetchall()
        
        for player in top_players:
            print(f"  {player[0]:<25} | {player[1]:<20} | H:{player[2]} R:{player[3]} RBI:{player[4]}")
        
        # Database Statistics
        print(f"\n📈 DATABASE STATISTICS:")
        stats = [
            ("Teams", "SELECT COUNT(*) FROM teams"),
            ("Games", "SELECT COUNT(*) FROM games"), 
            ("Players", "SELECT COUNT(*) FROM players"),
            ("Boxscore Records", "SELECT COUNT(*) FROM boxscore"),
            ("Raw JSON Backups", "SELECT COUNT(*) FROM raw_json_data")
        ]
        
        for stat_name, query in stats:
            count = conn.execute(text(query)).fetchone()[0]
            print(f"  {stat_name:<20}: {count:>5}")
        
        # Recent Data Loads
        print(f"\n🕒 RECENT DATA LOADS:")
        recent = conn.execute(text("""
            SELECT TOP 5 data_type, COUNT(*) as count, 
                   MAX(extraction_timestamp) as latest_load
            FROM raw_json_data 
            GROUP BY data_type
            ORDER BY latest_load DESC
        """)).fetchall()
        
        for load in recent:
            print(f"  {load[0]:<15} | Count: {load[1]:>2} | Latest: {load[2]}")
        
        conn.close()
        print("\n" + "=" * 60)
        print("✅ Database query completed successfully!")
        
    except Exception as e:
        print(f"❌ Error querying database: {e}")

if __name__ == "__main__":
    view_database_data()
