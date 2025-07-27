#!/usr/bin/env python3
"""
Check Boxscore Data for Doubles, Triples, Home Runs
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database.connection import DatabaseConnection

def check_boxscore_data():
    """Check if doubles, triples, and home runs data is properly populated."""
    db = DatabaseConnection()
    
    try:
        db.connect()
        
        print("📊 CHECKING BOXSCORE DATA FOR DOUBLES, TRIPLES, HOME RUNS")
        print("=" * 70)
        
        # 1. Check if columns exist
        print("1. Verifying columns exist:")
        result = db.fetch_results("""
        SELECT COLUMN_NAME
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = 'boxscore' AND COLUMN_NAME IN ('doubles', 'triples', 'home_runs')
        ORDER BY COLUMN_NAME
        """)
        columns_found = [row[0] for row in result]
        print(f"   Found columns: {columns_found}")
        
        # 2. Check total records
        total_records = db.fetch_results("SELECT COUNT(*) FROM boxscore")[0][0]
        print(f"2. Total boxscore records: {total_records}")
        
        # 3. Check for non-zero values in new columns
        print("3. Checking for non-zero values:")
        doubles_count = db.fetch_results("SELECT COUNT(*) FROM boxscore WHERE doubles > 0")[0][0]
        triples_count = db.fetch_results("SELECT COUNT(*) FROM boxscore WHERE triples > 0")[0][0]
        hr_count = db.fetch_results("SELECT COUNT(*) FROM boxscore WHERE home_runs > 0")[0][0]
        
        print(f"   Records with doubles > 0: {doubles_count}")
        print(f"   Records with triples > 0: {triples_count}")
        print(f"   Records with home_runs > 0: {hr_count}")
        
        # 4. Check for NULL values
        print("4. Checking for NULL values:")
        null_doubles = db.fetch_results("SELECT COUNT(*) FROM boxscore WHERE doubles IS NULL")[0][0]
        null_triples = db.fetch_results("SELECT COUNT(*) FROM boxscore WHERE triples IS NULL")[0][0]
        null_hrs = db.fetch_results("SELECT COUNT(*) FROM boxscore WHERE home_runs IS NULL")[0][0]
        
        print(f"   Records with NULL doubles: {null_doubles}")
        print(f"   Records with NULL triples: {null_triples}")
        print(f"   Records with NULL home_runs: {null_hrs}")
        
        # 5. Sample records with extra base hits
        print("5. Sample records with extra base hits:")
        sample = db.fetch_results("""
        SELECT TOP 10 game_id, player_id, at_bats, hits, doubles, triples, home_runs, rbi
        FROM boxscore
        WHERE (doubles > 0 OR triples > 0 OR home_runs > 0)
        ORDER BY (doubles + triples + home_runs) DESC
        """)
        
        if sample:
            print("   Game     Player   AB  H   2B  3B  HR  RBI")
            print("   " + "-" * 45)
            for row in sample:
                game_id, player_id, ab, h, doubles, triples, hr, rbi = row
                print(f"   {game_id:<8} {player_id:<8} {ab or 0:<3} {h or 0:<3} {doubles or 0:<3} {triples or 0:<3} {hr or 0:<3} {rbi or 0:<3}")
        else:
            print("   No records found with extra base hits!")
        
        # 6. Total statistics
        print("6. Total statistics:")
        totals = db.fetch_results("""
        SELECT 
            SUM(CASE WHEN doubles IS NULL THEN 0 ELSE doubles END) as total_doubles,
            SUM(CASE WHEN triples IS NULL THEN 0 ELSE triples END) as total_triples,
            SUM(CASE WHEN home_runs IS NULL THEN 0 ELSE home_runs END) as total_homeruns
        FROM boxscore
        """)[0]
        
        print(f"   Total doubles in database: {totals[0] or 0}")
        print(f"   Total triples in database: {totals[1] or 0}")
        print(f"   Total home runs in database: {totals[2] or 0}")
        
        # 7. Check if data was loaded before schema update
        print("7. Analysis:")
        if null_doubles == total_records and null_triples == total_records and null_hrs == total_records:
            print("   ❌ ISSUE: All values are NULL - data was loaded before schema update!")
            print("   💡 SOLUTION: Need to reload March data with updated schema")
        elif totals[0] == 0 and totals[1] == 0 and totals[2] == 0:
            print("   ❌ ISSUE: All values are 0 - data might not be extracting correctly!")
            print("   💡 SOLUTION: Check JSON parsing logic")
        else:
            print("   ✅ Data appears to be populated correctly!")
        
    except Exception as e:
        print(f"❌ Error checking boxscore data: {e}")
    
    finally:
        db.disconnect()

if __name__ == "__main__":
    check_boxscore_data()
