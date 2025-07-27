#!/usr/bin/env python3
"""
Show Top 10 Rows from dbo.games Table
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database.connection import DatabaseConnection

def show_top_10_games():
    """Display the top 10 rows from dbo.games table."""
    
    db = DatabaseConnection()
    try:
        db.connect()
        
        print("🏟️  TOP 10 ROWS FROM dbo.games")
        print("=" * 100)
        
        result = db.fetch_results("""
        SELECT TOP 10 
            game_id, 
            game_date, 
            home_team_id, 
            away_team_id, 
            home_score, 
            away_score, 
            game_type, 
            series_description,
            official_date,
            game_status
        FROM games 
        ORDER BY game_date DESC, game_id
        """)
        
        # Print header
        print(f"{'Game ID':<8} {'Date':<12} {'Home':<4} {'Away':<4} {'H-Score':<7} {'A-Score':<7} {'Type':<4} {'Series':<18} {'Official':<10} {'Status':<12}")
        print("-" * 100)
        
        # Print rows
        for row in result:
            game_id, game_date, home_id, away_id, home_score, away_score, game_type, series_desc, official_date, status = row
            print(f"{game_id:<8} {str(game_date):<12} {home_id or 'N/A':<4} {away_id or 'N/A':<4} {home_score or 0:<7} {away_score or 0:<7} {game_type or 'N/A':<4} {(series_desc or 'N/A')[:18]:<18} {str(official_date) if official_date else 'N/A':<10} {(status or 'N/A')[:12]:<12}")
        
        # Get total count
        count_result = db.fetch_results("SELECT COUNT(*) FROM games")
        total_count = count_result[0][0]
        
        print(f"\n📊 Total games in database: {total_count}")
        
        # Get count by game type
        print(f"\n🎮 Game Type Distribution:")
        type_result = db.fetch_results("""
        SELECT game_type, COUNT(*) as count 
        FROM games 
        GROUP BY game_type 
        ORDER BY COUNT(*) DESC
        """)
        
        for row in type_result:
            game_type, count = row
            type_name = {
                'R': 'Regular Season',
                'S': 'Spring Training', 
                'E': 'Exhibition',
                'A': 'All-Star Game'
            }.get(game_type, 'Unknown')
            print(f"   {game_type or 'NULL'}: {count} ({type_name})")
        
        # Get date range
        date_range = db.fetch_results("SELECT MIN(game_date), MAX(game_date) FROM games")[0]
        min_date, max_date = date_range
        print(f"\n📅 Date Range: {min_date} to {max_date}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.disconnect()

if __name__ == "__main__":
    show_top_10_games()
