#!/usr/bin/env python3
"""
Run MLB Season Phase Analysis
Execute the MLB season phase analysis SQL query and display results.
"""

import sys
from pathlib import Path

# Add src to path - go up one directory to find src
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from src.database.connection import DatabaseConnection

def run_mlb_season_phase_analysis():
    """Execute the MLB season phase analysis query."""
    
    db = DatabaseConnection()
    try:
        db.connect()
        
        print("🏟️  MLB SEASON PHASE ANALYSIS - 2025")
        print("=" * 60)
        
        # The SQL query from the file
        analysis_query = """
        -- MLB season phase analysis
        SELECT d.mlb_season_phase, AVG(home_score + away_score) as avg_total_runs
        FROM dim_date d
        JOIN dbo.games g ON CAST(g.official_date AS DATE) = d.full_date
        WHERE d.year = 2025
        GROUP BY d.mlb_season_phase;
        """
        
        print("📊 Executing query...")
        print("Query: Average total runs per game by MLB season phase in 2025")
        print("-" * 60)
        
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
            
            # Additional insights
            print(f"\n📈 INSIGHTS:")
            
            # Find highest and lowest scoring phases
            sorted_results = sorted(results, key=lambda x: x[1])
            if len(sorted_results) >= 2:
                lowest_phase, lowest_avg = sorted_results[0]
                highest_phase, highest_avg = sorted_results[-1]
                
                print(f"• Highest scoring phase: {highest_phase} ({highest_avg:.2f} runs/game)")
                print(f"• Lowest scoring phase: {lowest_phase} ({lowest_avg:.2f} runs/game)")
                
                if len(sorted_results) > 1:
                    difference = highest_avg - lowest_avg
                    print(f"• Difference: {difference:.2f} runs per game")
            
            # Show monthly breakdown for regular season
            print(f"\n📅 REGULAR SEASON MONTHLY BREAKDOWN:")
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
                for month, avg_runs, count in monthly_results:
                    print(f"{month:<12} {avg_runs:>8.2f} {count:>8}")
        
        else:
            print("❌ No results found. This could mean:")
            print("   • No games in 2025 in the database")
            print("   • Date join issues between dim_date and games tables")
            print("   • Missing data in either table")
        
        return True
        
    except Exception as e:
        print(f"❌ Error running MLB season phase analysis: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.disconnect()

if __name__ == "__main__":
    run_mlb_season_phase_analysis()
