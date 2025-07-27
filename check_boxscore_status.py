#!/usr/bin/env python3
"""
Check Boxscore Data Status
Quick script to check what boxscore data we currently have.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from src.database.connection import DatabaseConnection

def check_boxscore_status():
    """Check the current status of boxscore data."""
    
    db = DatabaseConnection()
    try:
        db.connect()
        
        print("📊 BOXSCORE DATA STATUS")
        print("=" * 50)
        
        # Check total boxscore records
        total_boxscore = db.fetch_results("SELECT COUNT(*) FROM boxscore")[0][0]
        print(f"Total boxscore records: {total_boxscore}")
        
        # Check by month
        monthly_boxscore = db.fetch_results("""
        SELECT 
            YEAR(g.game_date) as year,
            MONTH(g.game_date) as month,
            DATENAME(month, g.game_date) as month_name,
            COUNT(b.id) as boxscore_records,
            COUNT(DISTINCT g.game_id) as games_with_boxscore
        FROM games g
        LEFT JOIN boxscore b ON g.game_id = b.game_id
        WHERE YEAR(g.game_date) = 2025
        GROUP BY YEAR(g.game_date), MONTH(g.game_date), DATENAME(month, g.game_date)
        ORDER BY YEAR(g.game_date), MONTH(g.game_date)
        """)
        
        print(f"\nBoxscore data by month (2025):")
        print("Month           Boxscore Records    Games with Boxscore")
        print("-" * 55)
        
        for year, month, month_name, boxscore_count, games_count in monthly_boxscore:
            print(f"{month_name:<12} {boxscore_count:>15} {games_count:>19}")
        
        # Check enhanced stats (doubles, triples, home runs)
        enhanced_stats = db.fetch_results("""
        SELECT 
            DATENAME(month, g.game_date) as month_name,
            COUNT(b.id) as total_records,
            SUM(CASE WHEN b.doubles > 0 THEN 1 ELSE 0 END) as records_with_doubles,
            SUM(CASE WHEN b.triples > 0 THEN 1 ELSE 0 END) as records_with_triples,
            SUM(CASE WHEN b.home_runs > 0 THEN 1 ELSE 0 END) as records_with_hrs,
            SUM(ISNULL(b.doubles, 0)) as total_doubles,
            SUM(ISNULL(b.triples, 0)) as total_triples,
            SUM(ISNULL(b.home_runs, 0)) as total_hrs
        FROM games g
        INNER JOIN boxscore b ON g.game_id = b.game_id
        WHERE YEAR(g.game_date) = 2025
        GROUP BY MONTH(g.game_date), DATENAME(month, g.game_date)
        ORDER BY MONTH(g.game_date)
        """)
        
        print(f"\nEnhanced batting statistics by month:")
        print("Month        Records  Doubles  Triples  Home Runs  Total 2B  Total 3B  Total HR")
        print("-" * 80)
        
        for month_name, total, doubles_records, triples_records, hr_records, total_2b, total_3b, total_hr in enhanced_stats:
            print(f"{month_name:<10} {total:>8} {doubles_records:>8} {triples_records:>8} {hr_records:>10} {total_2b:>9} {total_3b:>9} {total_hr:>9}")
        
        # Check May data specifically
        may_status = db.fetch_results("""
        SELECT 
            COUNT(DISTINCT g.game_id) as may_games,
            COUNT(b.id) as may_boxscore_records
        FROM games g
        LEFT JOIN boxscore b ON g.game_id = b.game_id
        WHERE g.game_date >= '2025-05-01' AND g.game_date <= '2025-05-31'
        """)[0]
        
        print(f"\nMay 2025 specific status:")
        print(f"Games in May: {may_status[0]}")
        print(f"Boxscore records for May: {may_status[1]}")
        
        if may_status[0] > 0 and may_status[1] == 0:
            print("⚠️  May games exist but no boxscore data - need to extract and load detailed data")
        elif may_status[1] > 0:
            print("✅ May boxscore data exists")
        else:
            print("❌ No May data found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking boxscore status: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.disconnect()

if __name__ == "__main__":
    check_boxscore_status()
