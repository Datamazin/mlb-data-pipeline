#!/usr/bin/env python3
"""
Clear and Repopulate Database with March and April 2025 Data
"""

import os
import sys
import glob
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database.connection import DatabaseConnection
from database.json_to_sql_loader import JSONToSQLLoader

def clear_and_repopulate_database():
    """Clear database tables and repopulate with March and April 2025 data."""
    
    print("🚀 CLEARING AND REPOPULATING DATABASE")
    print("=" * 60)
    
    # Initialize database connection
    db = DatabaseConnection()
    
    try:
        db.connect()
        
        # 1. Clear all tables
        print("1. Clearing all database tables...")
        
        # Get counts before deletion
        games_before = db.fetch_results("SELECT COUNT(*) FROM games")[0][0]
        boxscore_before = db.fetch_results("SELECT COUNT(*) FROM boxscore")[0][0]
        players_before = db.fetch_results("SELECT COUNT(*) FROM players")[0][0]
        teams_before = db.fetch_results("SELECT COUNT(*) FROM teams")[0][0]
        
        print(f"   Records before deletion:")
        print(f"     Games: {games_before}")
        print(f"     Boxscore: {boxscore_before}")
        print(f"     Players: {players_before}")
        print(f"     Teams: {teams_before}")
        
        # Clear tables in proper order (respecting foreign keys)
        print("   Clearing boxscore table...")
        db.execute_query("DELETE FROM boxscore")
        
        print("   Clearing games table...")
        db.execute_query("DELETE FROM games")
        
        print("   Clearing players table...")
        db.execute_query("DELETE FROM players")
        
        print("   Clearing teams table...")
        db.execute_query("DELETE FROM teams")
        
        # Verify tables are empty
        games_after = db.fetch_results("SELECT COUNT(*) FROM games")[0][0]
        boxscore_after = db.fetch_results("SELECT COUNT(*) FROM boxscore")[0][0]
        players_after = db.fetch_results("SELECT COUNT(*) FROM players")[0][0]
        teams_after = db.fetch_results("SELECT COUNT(*) FROM teams")[0][0]
        
        print(f"   ✅ Tables cleared successfully!")
        print(f"     Games: {games_after}")
        print(f"     Boxscore: {boxscore_after}")
        print(f"     Players: {players_after}")
        print(f"     Teams: {teams_after}")
        
        # 2. Find all March and April combined data files
        print("\n2. Finding March and April data files...")
        
        march_data_path = Path("data/json/2025/03-March")
        april_data_path = Path("data/json/2025/04-April")
        
        march_files = list(march_data_path.glob("combined_data_*.json")) if march_data_path.exists() else []
        april_files = list(april_data_path.glob("combined_data_*.json")) if april_data_path.exists() else []
        
        march_files.sort()
        april_files.sort()
        
        print(f"   Found {len(march_files)} March files")
        print(f"   Found {len(april_files)} April files")
        print(f"   Total files to process: {len(march_files) + len(april_files)}")
        
        if not march_files and not april_files:
            print("❌ No data files found! Make sure data extraction was completed.")
            return
        
        # 3. Initialize JSON loader with enhanced schema
        loader = JSONToSQLLoader()
        
        # 4. Load March data
        if march_files:
            print(f"\n3. Loading {len(march_files)} March files...")
            
            march_success = 0
            march_errors = 0
            
            for i, file_path in enumerate(march_files, 1):
                try:
                    if i % 50 == 0 or i % 100 == 1:  # Progress update
                        print(f"   [{i}/{len(march_files)}] Loading {file_path.name}...")
                    
                    # Load the combined data file
                    success = loader.load_json_to_database(str(file_path))
                    if success:
                        march_success += 1
                    else:
                        march_errors += 1
                    
                except Exception as e:
                    print(f"   ❌ Error loading {file_path.name}: {e}")
                    march_errors += 1
            
            print(f"   March loading completed!")
            print(f"     ✅ Successfully loaded: {march_success} files")
            print(f"     ❌ Errors: {march_errors} files")
        
        # 5. Load April data
        if april_files:
            print(f"\n4. Loading {len(april_files)} April files...")
            
            april_success = 0
            april_errors = 0
            
            for i, file_path in enumerate(april_files, 1):
                try:
                    if i % 50 == 0 or i % 100 == 1:  # Progress update
                        print(f"   [{i}/{len(april_files)}] Loading {file_path.name}...")
                    
                    # Load the combined data file
                    success = loader.load_json_to_database(str(file_path))
                    if success:
                        april_success += 1
                    else:
                        april_errors += 1
                    
                except Exception as e:
                    print(f"   ❌ Error loading {file_path.name}: {e}")
                    april_errors += 1
            
            print(f"   April loading completed!")
            print(f"     ✅ Successfully loaded: {april_success} files")
            print(f"     ❌ Errors: {april_errors} files")
        
        # 6. Verify the loaded data
        print(f"\n5. Verifying loaded data...")
        
        # Check final counts
        final_games = db.fetch_results("SELECT COUNT(*) FROM games")[0][0]
        final_boxscore = db.fetch_results("SELECT COUNT(*) FROM boxscore")[0][0]
        final_players = db.fetch_results("SELECT COUNT(*) FROM players")[0][0]
        final_teams = db.fetch_results("SELECT COUNT(*) FROM teams")[0][0]
        
        print(f"   Final record counts:")
        print(f"     Games: {final_games}")
        print(f"     Boxscore: {final_boxscore}")
        print(f"     Players: {final_players}")
        print(f"     Teams: {final_teams}")
        
        # Check date ranges
        if final_games > 0:
            date_range = db.fetch_results("""
            SELECT MIN(game_date) as min_date, MAX(game_date) as max_date 
            FROM games
            """)[0]
            print(f"   Date range: {date_range[0]} to {date_range[1]}")
            
            # Check monthly breakdown
            monthly = db.fetch_results("""
            SELECT 
                YEAR(game_date) as year,
                MONTH(game_date) as month,
                COUNT(*) as game_count
            FROM games 
            GROUP BY YEAR(game_date), MONTH(game_date)
            ORDER BY year, month
            """)
            
            print(f"   Monthly breakdown:")
            month_names = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                         7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
            for row in monthly:
                year, month, count = row
                print(f"     {month_names[month]} {year}: {count} games")
        
        # Check enhanced batting stats
        if final_boxscore > 0:
            print(f"\n6. Checking enhanced batting statistics...")
            enhanced_stats = db.fetch_results("""
            SELECT 
                SUM(CASE WHEN doubles > 0 THEN 1 ELSE 0 END) as records_with_doubles,
                SUM(CASE WHEN triples > 0 THEN 1 ELSE 0 END) as records_with_triples,
                SUM(CASE WHEN home_runs > 0 THEN 1 ELSE 0 END) as records_with_hrs,
                SUM(CASE WHEN doubles IS NULL THEN 1 ELSE 0 END) as null_doubles,
                SUM(ISNULL(doubles, 0)) as total_doubles,
                SUM(ISNULL(triples, 0)) as total_triples,
                SUM(ISNULL(home_runs, 0)) as total_hrs
            FROM boxscore
            """)[0]
            
            print(f"   Enhanced batting statistics:")
            print(f"     Records with doubles: {enhanced_stats[0]}")
            print(f"     Records with triples: {enhanced_stats[1]}")
            print(f"     Records with home runs: {enhanced_stats[2]}")
            print(f"     NULL values: {enhanced_stats[3]}")
            print(f"     Total doubles: {enhanced_stats[4]}")
            print(f"     Total triples: {enhanced_stats[5]}")
            print(f"     Total home runs: {enhanced_stats[6]}")
            
            if enhanced_stats[3] == final_boxscore:
                print("   ❌ All enhanced stats are NULL - check JSON loader")
            elif enhanced_stats[4] > 0 or enhanced_stats[5] > 0 or enhanced_stats[6] > 0:
                print("   ✅ Enhanced batting stats loaded successfully!")
            else:
                print("   ⚠️  Enhanced stats are all zero - this might be normal")
        
        print(f"\n🎉 Database repopulation completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during database repopulation: {e}")
    
    finally:
        db.disconnect()

if __name__ == "__main__":
    clear_and_repopulate_database()
