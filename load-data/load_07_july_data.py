#!/usr/bin/env python3
"""
Load July 2025 Data with Enhanced Batting Statistics
"""

import os
import sys
import glob
from pathlib import Path

# Add the parent directory (project root) to the path since we're in load-data subdirectory
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.database.connection import DatabaseConnection
from src.database.json_to_sql_loader import JSONToSQLLoader

def load_july_data():
    """Load July 2025 data with enhanced batting statistics."""
    
    print("🚀 LOADING July 2025 DATA WITH ENHANCED BATTING STATS")
    print("=" * 60)
    
    # Initialize database connection
    db = DatabaseConnection()
    
    try:
        db.connect()
        
        # 1. First, check if we need to clear existing July data
        print("1. Checking existing July 2025 data...")
        existing_july = db.fetch_results("""
        SELECT COUNT(*) as count
        FROM games 
        WHERE game_date >= '2025-07-01' AND game_date <= '2025-07-31'
        """)[0][0]
        
        if existing_july > 0:
            print(f"   Found {existing_july} existing July games")
            print("   Clearing existing July data to reload with enhanced stats...")
            
            # Use transaction to clear data safely
            delete_queries = [
                """
                DELETE FROM boxscore 
                WHERE game_id IN (
                    SELECT game_id FROM games 
                    WHERE game_date >= '2025-07-01' AND game_date <= '2025-07-31'
                )
                """,
                """
                DELETE FROM games 
                WHERE game_date >= '2025-07-01' AND game_date <= '2025-07-31'
                """
            ]
            
            db.execute_transaction(delete_queries)
            print("   ✅ Existing July data cleared")
        else:
            print("   No existing July data found")

        # 2. Find all July combined data files
        july_data_path = Path("data/json/2025/07-July")
        combined_files = list(july_data_path.glob("combined_data_*.json"))
        combined_files.sort()

        print(f"\n2. Found {len(combined_files)} July combined data files")

        if not combined_files:
            print("❌ No July data files found! Run extraction first.")
            return
        
        # 3. Initialize JSON loader with enhanced schema
        loader = JSONToSQLLoader()
        
        # 4. Load each file
        print(f"\n3. Loading {len(combined_files)} files...")
        
        success_count = 0
        error_count = 0
        
        for i, file_path in enumerate(combined_files, 1):
            try:
                print(f"   [{i}/{len(combined_files)}] Loading {file_path.name}...")
                
                # Load the combined data file
                loader.load_json_to_database(str(file_path))
                success_count += 1
                
                if i % 50 == 0:  # Progress update every 50 files
                    print(f"   Progress: {i}/{len(combined_files)} files processed")
                
            except Exception as e:
                print(f"   ❌ Error loading {file_path.name}: {e}")
                error_count += 1
        
        print(f"\n4. Loading completed!")
        print(f"   ✅ Successfully loaded: {success_count} files")
        print(f"   ❌ Errors: {error_count} files")
        
        # 5. Verify the loaded data
        print(f"\n5. Verifying loaded data...")
        
        # Check games
        games_count = db.fetch_results("""
        SELECT COUNT(*) as count
        FROM games 
        WHERE game_date >= '2025-07-01' AND game_date <= '2025-07-31'
        """)[0][0]
        print(f"   Games loaded: {games_count}")
        
        # Check boxscore records
        boxscore_count = db.fetch_results("""
        SELECT COUNT(*) as count
        FROM boxscore b
        INNER JOIN games g ON b.game_id = g.game_id
        WHERE g.game_date >= '2025-07-01' AND g.game_date <= '2025-07-31'
        """)[0][0]
        print(f"   Boxscore records: {boxscore_count}")
        
        # Check enhanced batting stats
        enhanced_stats = db.fetch_results("""
        SELECT 
            SUM(CASE WHEN b.doubles > 0 THEN 1 ELSE 0 END) as records_with_doubles,
            SUM(CASE WHEN b.triples > 0 THEN 1 ELSE 0 END) as records_with_triples,
            SUM(CASE WHEN b.home_runs > 0 THEN 1 ELSE 0 END) as records_with_hrs,
            SUM(CASE WHEN b.doubles IS NULL THEN 1 ELSE 0 END) as null_doubles,
            SUM(ISNULL(b.doubles, 0)) as total_doubles,
            SUM(ISNULL(b.triples, 0)) as total_triples,
            SUM(ISNULL(b.home_runs, 0)) as total_hrs
        FROM boxscore b
        INNER JOIN games g ON b.game_id = g.game_id
        WHERE g.game_date >= '2025-07-01' AND g.game_date <= '2025-07-31'
        """)[0]
        
        print(f"   Enhanced batting statistics:")
        print(f"     Records with doubles: {enhanced_stats[0] or 0}")
        print(f"     Records with triples: {enhanced_stats[1] or 0}")
        print(f"     Records with home runs: {enhanced_stats[2] or 0}")
        print(f"     NULL values: {enhanced_stats[3] or 0}")
        print(f"     Total doubles: {enhanced_stats[4] or 0}")
        print(f"     Total triples: {enhanced_stats[5] or 0}")
        print(f"     Total home runs: {enhanced_stats[6] or 0}")
        
        if (enhanced_stats[3] or 0) == boxscore_count and boxscore_count > 0:
            print("   ❌ All enhanced stats are NULL - check JSON loader")
        elif (enhanced_stats[4] or 0) > 0 or (enhanced_stats[5] or 0) > 0 or (enhanced_stats[6] or 0) > 0:
            print("   ✅ Enhanced batting stats loaded successfully!")
        else:
            print("   ⚠️  Enhanced stats are all zero - this might be normal")

        print(f"\n🎉 July 2025 data loading completed successfully!")

    except Exception as e:
        print(f"❌ Error loading July data: {e}")

    finally:
        db.disconnect()

if __name__ == "__main__":
    load_july_data()
