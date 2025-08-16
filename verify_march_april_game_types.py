#!/usr/bin/env python3
"""
Verify March and April 2025 Game Type Data
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database.connection import DatabaseConnection

def verify_march_april_game_types():
    """Verify that March and April 2025 games have proper game type data."""
    
    print("🔍 VERIFYING MARCH & APRIL 2025 GAME TYPE DATA")
    print("=" * 70)
    
    db = DatabaseConnection()
    try:
        db.connect()
        
        # 1. Overall statistics
        print("1. OVERALL GAME TYPE DISTRIBUTION:")
        result = db.fetch_results("""
        SELECT 
            game_type,
            COUNT(*) as count,
            MIN(game_date) as earliest_date,
            MAX(game_date) as latest_date
        FROM games 
        WHERE game_date >= '2025-03-01' AND game_date <= '2025-04-30'
        GROUP BY game_type 
        ORDER BY COUNT(*) DESC
        """)
        
        total_games = sum(row[1] for row in result)
        
        if total_games == 0:
            print(f"   ❌ No games found in March & April 2025")
            print(f"   💡 This may indicate that the games table needs to be populated first")
            print(f"   📅 Expected date range: 2025-03-01 to 2025-04-30")
            return
        
        game_type_names = {
            'R': 'Regular Season',
            'S': 'Spring Training', 
            'E': 'Exhibition',
            'A': 'All-Star Game',
            'D': 'Division Series',
            'F': 'Wild Card Game',
            'L': 'League Championship',
            'W': 'World Series'
        }
        
        print(f"   Type  Description        Count   %      Date Range")
        print(f"   " + "-" * 60)
        for row in result:
            game_type, count, earliest, latest = row
            percentage = (count / total_games) * 100 if total_games > 0 else 0
            type_name = game_type_names.get(game_type, 'Unknown')
            print(f"   {game_type or 'NULL':<5} {type_name:<18} {count:<7} {percentage:5.1f}%  {earliest} to {latest}")
        
        print(f"\n   Total: {total_games} games")
        
        # 2. Monthly breakdown
        print(f"\n2. MONTHLY BREAKDOWN:")
        monthly = db.fetch_results("""
        SELECT 
            YEAR(game_date) as year,
            MONTH(game_date) as month,
            game_type,
            COUNT(*) as count
        FROM games 
        WHERE game_date >= '2025-03-01' AND game_date <= '2025-04-30'
        GROUP BY YEAR(game_date), MONTH(game_date), game_type
        ORDER BY year, month, game_type
        """)
        
        month_names = {3: 'March', 4: 'April'}
        current_month = None
        
        for row in monthly:
            year, month, game_type, count = row
            if month != current_month:
                current_month = month
                print(f"\n   {month_names[month]} {year}:")
            
            type_name = game_type_names.get(game_type, 'Unknown')
            print(f"     {game_type}: {count} {type_name} games")
        
        # 3. Sample games with game type
        print(f"\n3. SAMPLE GAMES WITH GAME TYPE:")
        sample = db.fetch_results("""
        SELECT TOP 10 
            game_id, 
            game_date, 
            game_type, 
            series_description,
            official_date,
            game_status
        FROM games 
        WHERE game_date >= '2025-03-01' AND game_date <= '2025-04-30'
        ORDER BY game_date DESC, game_id
        """)
        
        print(f"   Game ID    Date       Type  Series              Official    Status")
        print(f"   " + "-" * 75)
        for row in sample:
            game_id, game_date, game_type, series_desc, official_date, status = row
            print(f"   {game_id:<10} {game_date} {game_type or 'N/A':<4}  {(series_desc or 'N/A')[:18]:<18} {official_date or 'N/A':<10} {status or 'N/A'}")
        
        # 4. Validation checks
        print(f"\n4. VALIDATION CHECKS:")
        
        # Check for missing game types
        null_types = db.fetch_results("""
        SELECT COUNT(*) FROM games 
        WHERE game_date >= '2025-03-01' AND game_date <= '2025-04-30' 
        AND game_type IS NULL
        """)[0][0]
        
        if null_types == 0:
            print(f"   ✅ All games have game_type populated (0 NULL values)")
        else:
            print(f"   ❌ {null_types} games missing game_type")
        
        # Check for proper date ranges
        date_check = db.fetch_results("""
        SELECT 
            MIN(game_date) as min_date,
            MAX(game_date) as max_date,
            COUNT(*) as total_games
        FROM games 
        WHERE game_date >= '2025-03-01' AND game_date <= '2025-04-30'
        """)[0]
        
        min_date, max_date, total = date_check
        print(f"   📅 Date range: {min_date} to {max_date} ({total} games)")
        
        if total == 0:
            print(f"   ❌ No games found in the specified date range")
        elif min_date and max_date:
            start_date = datetime.strptime('2025-03-01', '%Y-%m-%d').date()
            end_date = datetime.strptime('2025-04-30', '%Y-%m-%d').date()
            if min_date >= start_date and max_date <= end_date:
                print(f"   ✅ All games within expected date range")
            else:
                print(f"   ⚠️  Some games outside expected date range")
        else:
            print(f"   ⚠️  Unable to verify date range (NULL dates returned)")
        
        # Check for reasonable game type distribution
        regular_season_count = db.fetch_results("""
        SELECT COUNT(*) FROM games 
        WHERE game_date >= '2025-03-01' AND game_date <= '2025-04-30' 
        AND game_type = 'R'
        """)[0][0]
        
        if regular_season_count > 0:
            print(f"   ✅ Found {regular_season_count} Regular Season games")
        else:
            print(f"   ⚠️  No Regular Season games found")
        
        print(f"\n🎉 VERIFICATION COMPLETE!")
        if total > 0:
            print(f"✅ dbo.games table successfully repopulated with game type data")
            print(f"✅ March & April 2025: {total} games with proper metadata")
        else:
            print(f"❌ No games found in March & April 2025 date range")
            print(f"💡 This may indicate that the games table needs to be populated first")
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.disconnect()

if __name__ == "__main__":
    from datetime import datetime
    verify_march_april_game_types()
