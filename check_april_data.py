#!/usr/bin/env python3
"""
Check April 2025 Data Coverage
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database.connection import DatabaseConnection

def check_april_data():
    """Check April 2025 data coverage."""
    db = DatabaseConnection()
    
    try:
        db.connect()
        
        print("📊 CHECKING APRIL 2025 DATA COVERAGE")
        print("=" * 50)
        
        # Check overall data range
        print("1. Overall data range:")
        overall = db.fetch_results("""
        SELECT COUNT(*) as total_games, 
               MIN(game_date) as min_date, 
               MAX(game_date) as max_date 
        FROM games
        """)[0]
        print(f"   Total games: {overall[0]}")
        print(f"   Date range: {overall[1]} to {overall[2]}")
        
        # Check April 2025 specifically
        print("\n2. April 2025 data:")
        april = db.fetch_results("""
        SELECT COUNT(*) as april_games,
               MIN(game_date) as min_april,
               MAX(game_date) as max_april
        FROM games 
        WHERE game_date >= '2025-04-01' AND game_date <= '2025-04-30'
        """)[0]
        print(f"   April games: {april[0]}")
        if april[0] > 0:
            print(f"   April date range: {april[1]} to {april[2]}")
        
        # Check monthly breakdown
        print("\n3. Monthly breakdown:")
        monthly = db.fetch_results("""
        SELECT 
            YEAR(game_date) as year,
            MONTH(game_date) as month,
            COUNT(*) as game_count
        FROM games 
        GROUP BY YEAR(game_date), MONTH(game_date)
        ORDER BY year, month
        """)
        
        for row in monthly:
            year, month, count = row
            month_names = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                         7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
            print(f"   {month_names[month]} {year}: {count} games")
        
        # Check boxscore data for April
        print("\n4. April 2025 boxscore data:")
        april_boxscore = db.fetch_results("""
        SELECT COUNT(*) as boxscore_records
        FROM boxscore b
        INNER JOIN games g ON b.game_id = g.game_id
        WHERE g.game_date >= '2025-04-01' AND g.game_date <= '2025-04-30'
        """)[0]
        print(f"   April boxscore records: {april_boxscore[0]}")
        
        # Check enhanced batting stats for April
        if april_boxscore[0] > 0:
            print("\n5. April 2025 enhanced batting stats:")
            april_stats = db.fetch_results("""
            SELECT 
                COUNT(*) as total_records,
                SUM(CASE WHEN b.doubles > 0 THEN 1 ELSE 0 END) as records_with_doubles,
                SUM(CASE WHEN b.triples > 0 THEN 1 ELSE 0 END) as records_with_triples,
                SUM(CASE WHEN b.home_runs > 0 THEN 1 ELSE 0 END) as records_with_hrs,
                SUM(CASE WHEN b.doubles IS NULL THEN 1 ELSE 0 END) as null_doubles,
                SUM(ISNULL(b.doubles, 0)) as total_doubles,
                SUM(ISNULL(b.triples, 0)) as total_triples,
                SUM(ISNULL(b.home_runs, 0)) as total_hrs
            FROM boxscore b
            INNER JOIN games g ON b.game_id = g.game_id
            WHERE g.game_date >= '2025-04-01' AND g.game_date <= '2025-04-30'
            """)[0]
            
            print(f"   Total player records: {april_stats[0]}")
            print(f"   Records with doubles: {april_stats[1]}")
            print(f"   Records with triples: {april_stats[2]}")
            print(f"   Records with home runs: {april_stats[3]}")
            print(f"   NULL values: {april_stats[4]}")
            print(f"   Total doubles: {april_stats[5]}")
            print(f"   Total triples: {april_stats[6]}")
            print(f"   Total home runs: {april_stats[7]}")
            
            if april_stats[4] == april_stats[0]:
                print("   ❌ All April data has NULL enhanced stats - needs reload!")
            elif april_stats[5] > 0 or april_stats[6] > 0 or april_stats[7] > 0:
                print("   ✅ April enhanced stats look good!")
            else:
                print("   ⚠️  April enhanced stats are all zero - check data")
        
    except Exception as e:
        print(f"❌ Error checking April data: {e}")
    
    finally:
        db.disconnect()

if __name__ == "__main__":
    check_april_data()
