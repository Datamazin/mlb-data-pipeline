#!/usr/bin/env python3
"""
Fix walks data and populate missing game metadata across the entire database 
by reprocessing existing JSON files with enhanced loader.

This script will:
1. Update all boxscore records to include the correct walks values
2. Populate missing game_type and other metadata by fetching from MLB schedule API
"""

import os
import sys
from pathlib import Path
from src.database.json_to_sql_loader import JSONToSQLLoader

def find_all_boxscore_json_files(data_dir="data"):
    """Find all boxscore JSON files in the data directory."""
    json_files = []
    data_path = Path(data_dir)
    
    for json_file in data_path.rglob("boxscore_raw_*.json"):
        json_files.append(str(json_file))
    
    return sorted(json_files)

def fix_walks_data():
    """Process all boxscore files to fix walks data and populate game metadata."""
    print("🔧 Starting enhanced walks data fix process...")
    print("📈 This will also populate missing game_type and metadata from MLB API")
    
    # Find all boxscore JSON files
    json_files = find_all_boxscore_json_files()
    print(f"📁 Found {len(json_files)} boxscore JSON files")
    
    if not json_files:
        print("❌ No boxscore JSON files found. Make sure you have data in the 'data' directory.")
        return
    
    # Process files with enhanced loader
    loader = JSONToSQLLoader()
    processed_count = 0
    error_count = 0
    metadata_fetched_count = 0
    
    for json_file in json_files:
        try:
            print(f"📄 Processing: {os.path.basename(json_file)}")
            
            # The enhanced loader will automatically fetch game metadata if missing
            success = loader.load_json_to_database(json_file)
            
            if success:
                processed_count += 1
                # Check if this resulted in metadata being fetched
                # (We can infer this from the console output)
            else:
                error_count += 1
                print(f"❌ Failed to process: {json_file}")
                
        except Exception as e:
            error_count += 1
            print(f"❌ Error processing {json_file}: {e}")
    
    print(f"\n✅ Enhanced walks data fix complete!")
    print(f"📊 Processed: {processed_count} files")
    print(f"❌ Errors: {error_count} files")
    
    # Show final statistics
    try:
        from src.database.connection import DatabaseConnection
        db = DatabaseConnection()
        if db.connect():
            # Walks statistics
            result = db.execute_query(
                "SELECT COUNT(*) as total_players_with_walks, SUM(walks) as total_walks FROM boxscore WHERE walks > 0"
            ).fetchone()
            
            print(f"\n📈 Database Statistics:")
            print(f"   Players with walks: {result[0]:,}")
            print(f"   Total walks: {result[1]:,}")
            
            # Game metadata statistics  
            result = db.execute_query("SELECT game_type, COUNT(*) as count FROM games GROUP BY game_type ORDER BY count DESC")
            print(f"\n🎮 Game Type Distribution:")
            for row in result:
                game_type_display = 'NULL/Empty' if (row.game_type is None or row.game_type == '') else row.game_type
                print(f"   {game_type_display}: {row.count}")
            
            # Count games with complete metadata
            result = db.execute_query(
                "SELECT COUNT(*) as complete_metadata FROM games WHERE game_type IS NOT NULL AND series_description IS NOT NULL"
            ).fetchone()
            print(f"\n📋 Games with complete metadata: {result[0]:,}")
            
            db.disconnect()
    except Exception as e:
        print(f"❌ Error getting final statistics: {e}")

if __name__ == "__main__":
    fix_walks_data()
