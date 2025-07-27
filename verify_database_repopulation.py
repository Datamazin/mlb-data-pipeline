#!/usr/bin/env python3
"""
Verify Database Repopulation - March and April 2025 Data
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database.connection import DatabaseConnection

def verify_database_repopulation():
    """Verify the database was properly repopulated with March and April data."""
    
    print("🔍 VERIFYING DATABASE REPOPULATION")
    print("=" * 60)
    
    db = DatabaseConnection()
    
    try:
        db.connect()
        
        # 1. Check record counts
        print("1. Record Counts:")
        games_count = db.fetch_results("SELECT COUNT(*) FROM games")[0][0]
        boxscore_count = db.fetch_results("SELECT COUNT(*) FROM boxscore")[0][0]
        players_count = db.fetch_results("SELECT COUNT(*) FROM players")[0][0]
        teams_count = db.fetch_results("SELECT COUNT(*) FROM teams")[0][0]
        
        print(f"   Games: {games_count}")
        print(f"   Boxscore: {boxscore_count}")
        print(f"   Players: {players_count}")
        print(f"   Teams: {teams_count}")
        
        # 2. Check date ranges
        if games_count > 0:
            print("\n2. Date Analysis:")
            date_range = db.fetch_results("""
            SELECT MIN(game_date) as min_date, MAX(game_date) as max_date 
            FROM games
            """)[0]
            print(f"   Date range: {date_range[0]} to {date_range[1]}")
            
            # Monthly breakdown
            monthly = db.fetch_results("""
            SELECT 
                YEAR(game_date) as year,
                MONTH(game_date) as month,
                COUNT(*) as game_count
            FROM games 
            GROUP BY YEAR(game_date), MONTH(game_date)
            ORDER BY year, month
            """)
            
            month_names = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                         7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
            
            print(f"   Monthly breakdown:")
            for row in monthly:
                year, month, count = row
                print(f"     {month_names[month]} {year}: {count} games")
        
        # 3. Check enhanced batting statistics
        if boxscore_count > 0:
            print("\n3. Enhanced Batting Statistics:")
            enhanced_stats = db.fetch_results("""
            SELECT 
                COUNT(*) as total_records,
                SUM(CASE WHEN doubles > 0 THEN 1 ELSE 0 END) as records_with_doubles,
                SUM(CASE WHEN triples > 0 THEN 1 ELSE 0 END) as records_with_triples,
                SUM(CASE WHEN home_runs > 0 THEN 1 ELSE 0 END) as records_with_hrs,
                SUM(CASE WHEN doubles IS NULL THEN 1 ELSE 0 END) as null_doubles,
                SUM(ISNULL(doubles, 0)) as total_doubles,
                SUM(ISNULL(triples, 0)) as total_triples,
                SUM(ISNULL(home_runs, 0)) as total_hrs
            FROM boxscore
            """)[0]
            
            total_records, records_doubles, records_triples, records_hrs, null_doubles, total_doubles, total_triples, total_hrs = enhanced_stats
            
            print(f"   Total boxscore records: {total_records}")
            print(f"   Records with doubles: {records_doubles}")
            print(f"   Records with triples: {records_triples}")
            print(f"   Records with home runs: {records_hrs}")
            print(f"   NULL doubles: {null_doubles}")
            print(f"   Total doubles: {total_doubles}")
            print(f"   Total triples: {total_triples}")
            print(f"   Total home runs: {total_hrs}")
            
            # Percentage analysis
            if total_records > 0:
                doubles_pct = (records_doubles / total_records) * 100
                triples_pct = (records_triples / total_records) * 100
                hrs_pct = (records_hrs / total_records) * 100
                
                print(f"\n   Statistical Analysis:")
                print(f"     % of records with doubles: {doubles_pct:.1f}%")
                print(f"     % of records with triples: {triples_pct:.1f}%")
                print(f"     % of records with home runs: {hrs_pct:.1f}%")
        
        # 4. Sample high-performing records
        print("\n4. Sample High-Performance Records:")
        sample_records = db.fetch_results("""
        SELECT TOP 10 
            g.game_date,
            b.game_id, 
            b.player_id, 
            b.at_bats, 
            b.hits, 
            b.doubles, 
            b.triples, 
            b.home_runs, 
            b.rbi,
            (ISNULL(b.doubles, 0) + ISNULL(b.triples, 0) + ISNULL(b.home_runs, 0)) as extra_base_hits
        FROM boxscore b
        JOIN games g ON b.game_id = g.game_id
        WHERE (b.doubles > 0 OR b.triples > 0 OR b.home_runs > 0)
        ORDER BY (ISNULL(b.doubles, 0) + ISNULL(b.triples, 0) + ISNULL(b.home_runs, 0)) DESC, b.rbi DESC
        """)
        
        if sample_records:
            print("   Date       Game     Player   AB  H   2B  3B  HR  RBI  XBH")
            print("   " + "-" * 60)
            for row in sample_records:
                date, game_id, player_id, ab, h, doubles, triples, hr, rbi, xbh = row
                print(f"   {date}  {game_id:<8} {player_id:<8} {ab or 0:<3} {h or 0:<3} {doubles or 0:<3} {triples or 0:<3} {hr or 0:<3} {rbi or 0:<3} {xbh or 0:<3}")
        
        # 5. Data integrity checks
        print("\n5. Data Integrity Checks:")
        
        # Check for orphaned records
        orphaned_boxscore = db.fetch_results("""
        SELECT COUNT(*) FROM boxscore b
        LEFT JOIN games g ON b.game_id = g.game_id
        WHERE g.game_id IS NULL
        """)[0][0]
        
        orphaned_games = db.fetch_results("""
        SELECT COUNT(*) FROM games g
        LEFT JOIN boxscore b ON g.game_id = b.game_id
        WHERE b.game_id IS NULL
        """)[0][0]
        
        print(f"   Orphaned boxscore records: {orphaned_boxscore}")
        print(f"   Games without boxscore: {orphaned_games}")
        
        # Check for correct date parsing
        future_games = db.fetch_results("""
        SELECT COUNT(*) FROM games 
        WHERE game_date > GETDATE()
        """)[0][0]
        
        print(f"   Games with future dates: {future_games}")
        
        # 6. Summary
        print("\n6. Summary:")
        if games_count > 800 and boxscore_count > 20000:
            print("   ✅ Record counts look healthy")
        else:
            print("   ⚠️  Record counts seem low")
            
        if null_doubles == 0:
            print("   ✅ No NULL values in enhanced batting stats")
        else:
            print("   ❌ Some enhanced batting stats are NULL")
            
        if orphaned_boxscore == 0 and orphaned_games == 0:
            print("   ✅ No orphaned records detected")
        else:
            print("   ⚠️  Orphaned records detected")
            
        if future_games == 0:
            print("   ✅ All game dates are historical (proper date parsing)")
        else:
            print("   ❌ Some games have future dates (date parsing issue)")
            
        if total_doubles > 2000 and total_hrs > 1500:
            print("   ✅ Enhanced batting statistics populated successfully")
        else:
            print("   ⚠️  Enhanced batting statistics seem low")
        
        print(f"\n🎉 Database verification completed!")
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
    
    finally:
        db.disconnect()

if __name__ == "__main__":
    verify_database_repopulation()
