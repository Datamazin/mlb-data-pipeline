#!/usr/bin/env python3
"""
Run Updated MLB Season Phase Analysis
Execute the MLB season phase analysis including May 2025 data.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from src.database.connection import DatabaseConnection

def run_updated_mlb_season_analysis():
    """Execute the updated MLB season phase analysis with May 2025 data."""
    
    db = DatabaseConnection()
    try:
        db.connect()
        
        print("🏟️  UPDATED MLB SEASON PHASE ANALYSIS - 2025")
        print("🆕 Now includes May 2025 data!")
        print("=" * 70)
        
        # The main analysis query
        analysis_query = """
        -- MLB season phase analysis with May data
        SELECT d.mlb_season_phase, AVG(home_score + away_score) as avg_total_runs
        FROM dim_date d
        JOIN dbo.games g ON CAST(g.official_date AS DATE) = d.full_date
        WHERE d.year = 2025
        GROUP BY d.mlb_season_phase;
        """
        
        print("📊 Executing query...")
        print("Query: Average total runs per game by MLB season phase in 2025")
        print("-" * 70)
        
        results = db.fetch_results(analysis_query)
        
        if results:
            print("MLB Season Phase           Average Total Runs")
            print("-" * 50)
            
            total_games = 0
            weighted_avg = 0
            
            for phase, avg_runs in results:
                # Get game count for this phase
                count_query = f"""
                SELECT COUNT(*) 
                FROM dim_date d
                JOIN dbo.games g ON CAST(g.official_date AS DATE) = d.full_date
                WHERE d.year = 2025 AND d.mlb_season_phase = '{phase}'
                """
                game_count = db.fetch_results(count_query)[0][0]
                
                total_games += game_count
                weighted_avg += avg_runs * game_count
                
                print(f"{phase:<25} {avg_runs:>8.2f} ({game_count} games)")
            
            # Calculate overall average
            if total_games > 0:
                overall_avg = weighted_avg / total_games
                print("-" * 50)
                print(f"{'Overall Average':<25} {overall_avg:>8.2f} ({total_games} total games)")
            
            # Show what's new with May data
            print(f"\n🆕 MAY 2025 DATA IMPACT:")
            may_games = db.fetch_results("""
            SELECT COUNT(*) FROM dbo.games 
            WHERE official_date >= '2025-05-01' AND official_date < '2025-06-01'
            """)[0][0]
            
            may_avg = db.fetch_results("""
            SELECT AVG(CAST(home_score + away_score AS FLOAT))
            FROM dbo.games 
            WHERE official_date >= '2025-05-01' AND official_date < '2025-06-01'
            """)[0][0]
            
            print(f"• May 2025 games added: {may_games}")
            print(f"• May 2025 average runs: {may_avg:.2f} per game")
            
            # Complete monthly breakdown for regular season
            print(f"\n📅 COMPLETE REGULAR SEASON MONTHLY BREAKDOWN:")
            monthly_query = """
            SELECT 
                d.month_name,
                AVG(g.home_score + g.away_score) as avg_runs,
                COUNT(*) as game_count
            FROM dim_date d
            JOIN dbo.games g ON CAST(g.official_date AS DATE) = d.full_date
            WHERE d.year = 2025 AND d.mlb_season_phase = 'Regular Season'
            GROUP BY d.month, d.month_name
            ORDER BY d.month
            """
            
            monthly_results = db.fetch_results(monthly_query)
            if monthly_results:
                print("Month           Avg Runs    Games")
                print("-" * 35)
                total_reg_games = 0
                total_reg_runs = 0
                for month, avg_runs, count in monthly_results:
                    print(f"{month:<12} {avg_runs:>8.2f} {count:>8}")
                    total_reg_games += count
                    total_reg_runs += avg_runs * count
                
                if total_reg_games > 0:
                    overall_reg_avg = total_reg_runs / total_reg_games
                    print("-" * 35)
                    print(f"{'Total':<12} {overall_reg_avg:>8.2f} {total_reg_games:>8}")
            
            # Database summary
            print(f"\n📊 DATABASE SUMMARY:")
            total_db_games = db.fetch_results("SELECT COUNT(*) FROM dbo.games WHERE YEAR(official_date) = 2025")[0][0]
            date_range = db.fetch_results("""
            SELECT MIN(official_date), MAX(official_date) 
            FROM dbo.games 
            WHERE YEAR(official_date) = 2025
            """)[0]
            
            print(f"• Total 2025 games in database: {total_db_games}")
            print(f"• Date range: {date_range[0]} to {date_range[1]}")
            
            # Show game type distribution
            game_type_dist = db.fetch_results("""
            SELECT 
                CASE 
                    WHEN game_type = 'R' THEN 'Regular Season'
                    WHEN game_type = 'S' THEN 'Spring Training'
                    WHEN game_type = 'E' THEN 'Exhibition'
                    ELSE game_type 
                END as game_type_name,
                COUNT(*) as count
            FROM dbo.games 
            WHERE YEAR(official_date) = 2025
            GROUP BY game_type
            ORDER BY COUNT(*) DESC
            """)
            
            print(f"• Game type distribution:")
            for game_type_name, count in game_type_dist:
                print(f"  {game_type_name}: {count} games")
        
        else:
            print("❌ No results found. Check if games and date dimension tables are properly joined.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error running updated MLB analysis: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.disconnect()

if __name__ == "__main__":
    run_updated_mlb_season_analysis()
