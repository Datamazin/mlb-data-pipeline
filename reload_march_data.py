#!/usr/bin/env python3
"""
Reload March 2025 Data with Enhanced Schema
This will reload the boxscore data to populate doubles, triples, and home runs.
"""

import os
import sys
import glob
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database.connection import DatabaseConnection
from database.json_to_sql_loader import JSONToSQLLoader

def clear_march_boxscore_data():
    """Clear existing March 2025 boxscore data so we can reload with new columns."""
    db = DatabaseConnection()
    
    try:
        db.connect()
        
        print("🗑️  Clearing existing March 2025 boxscore data...")
        
        # Get March 2025 game IDs
        march_games = db.fetch_results("""
        SELECT DISTINCT game_id 
        FROM games 
        WHERE game_date >= '2025-03-01' AND game_date <= '2025-03-31'
        """)
        
        game_ids = [str(game[0]) for game in march_games]
        print(f"   Found {len(game_ids)} March 2025 games")
        
        if game_ids:
            # Delete boxscore records for March games
            placeholders = ','.join(['?' for _ in game_ids])
            query = f"DELETE FROM boxscore WHERE game_id IN ({placeholders})"
            
            # Convert to SQL Server parameter format
            sql_query = query.replace('?', ':param{}')
            params = {f'param{i}': game_id for i, game_id in enumerate(game_ids)}
            
            # Use a simpler approach with IN clause
            game_ids_str = ','.join(game_ids)
            simple_query = f"DELETE FROM boxscore WHERE game_id IN ({game_ids_str})"
            
            result = db.execute_query(simple_query)
            print("   ✅ Cleared existing boxscore data for March 2025")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error clearing data: {e}")
        return False
    
    finally:
        db.disconnect()

def reload_march_boxscore_data():
    """Reload March 2025 data with the enhanced schema."""
    
    print("🔄 RELOADING MARCH 2025 DATA WITH ENHANCED SCHEMA")
    print("=" * 60)
    
    # Step 1: Clear existing boxscore data
    if not clear_march_boxscore_data():
        print("❌ Failed to clear existing data")
        return False
    
    # Step 2: Reload the data
    print("\n📂 Reloading March 2025 combined data files...")
    
    # Get all combined data files from March 2025
    march_files = sorted(glob.glob('data/json/2025/03-March/combined_data_*.json'))
    total_files = len(march_files)
    
    print(f"   Found {total_files} combined data files")
    
    # Initialize the loader
    loader = JSONToSQLLoader()
    
    # Counters
    success_count = 0
    error_count = 0
    
    # Process each file
    for i, file_path in enumerate(march_files, 1):
        filename = os.path.basename(file_path)
        
        try:
            if i % 50 == 0 or i == 1:
                print(f"[{i:3d}/{total_files}] Processing {filename}...")
            
            # Load the file
            result = loader.load_json_to_database(file_path)
            
            if result:
                success_count += 1
            else:
                error_count += 1
                print(f"             ❌ Failed to load {filename}")
                
        except Exception as e:
            error_count += 1
            print(f"             ❌ Error loading {filename}: {str(e)}")
        
        # Progress update every 100 files
        if i % 100 == 0:
            print(f"   Progress: {i}/{total_files} processed ({success_count} success, {error_count} errors)")
    
    # Final summary
    print(f"\n📊 RELOAD RESULTS:")
    print(f"   📁 Total files: {total_files}")
    print(f"   ✅ Successfully loaded: {success_count}")
    print(f"   ❌ Failed to load: {error_count}")
    print(f"   📈 Success rate: {(success_count/total_files)*100:.1f}%")
    
    # Step 3: Verify the data
    print(f"\n🔍 Verifying enhanced data...")
    
    db = DatabaseConnection()
    try:
        db.connect()
        
        # Check for non-zero values
        doubles_count = db.fetch_results("SELECT COUNT(*) FROM boxscore WHERE doubles > 0")[0][0]
        triples_count = db.fetch_results("SELECT COUNT(*) FROM boxscore WHERE triples > 0")[0][0]
        hr_count = db.fetch_results("SELECT COUNT(*) FROM boxscore WHERE home_runs > 0")[0][0]
        
        print(f"   Records with doubles > 0: {doubles_count}")
        print(f"   Records with triples > 0: {triples_count}")
        print(f"   Records with home_runs > 0: {hr_count}")
        
        # Get totals
        totals = db.fetch_results("""
        SELECT 
            SUM(CASE WHEN doubles IS NULL THEN 0 ELSE doubles END) as total_doubles,
            SUM(CASE WHEN triples IS NULL THEN 0 ELSE triples END) as total_triples,
            SUM(CASE WHEN home_runs IS NULL THEN 0 ELSE home_runs END) as total_homeruns
        FROM boxscore
        """)[0]
        
        print(f"   Total doubles: {totals[0] or 0}")
        print(f"   Total triples: {totals[1] or 0}")
        print(f"   Total home runs: {totals[2] or 0}")
        
        if totals[0] > 0 or totals[1] > 0 or totals[2] > 0:
            print("\n✅ SUCCESS: Enhanced batting statistics are now populated!")
        else:
            print("\n❌ ISSUE: Still no extra base hit data found")
            
    except Exception as e:
        print(f"❌ Error verifying data: {e}")
    
    finally:
        db.disconnect()
    
    return success_count > 0

if __name__ == "__main__":
    success = reload_march_boxscore_data()
    if success:
        print("\n🎉 March 2025 data reload completed with enhanced schema!")
    else:
        print("\n❌ Failed to reload March 2025 data")
