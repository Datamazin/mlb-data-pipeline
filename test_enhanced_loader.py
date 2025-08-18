#!/usr/bin/env python3
"""
Test the enhanced loader with a few files to verify it works correctly.
"""

import os
from pathlib import Path
from src.database.json_to_sql_loader import JSONToSQLLoader

def test_enhanced_loader():
    """Test the enhanced loader with a few files."""
    print("🧪 Testing enhanced loader...")
    
    # Find first 3 boxscore files
    data_path = Path("data")
    json_files = []
    for json_file in data_path.rglob("boxscore_raw_*.json"):
        json_files.append(str(json_file))
        if len(json_files) >= 3:
            break
    
    print(f"📁 Testing with {len(json_files)} files")
    
    loader = JSONToSQLLoader()
    
    for json_file in json_files:
        print(f"\n📄 Processing: {os.path.basename(json_file)}")
        try:
            success = loader.load_json_to_database(json_file)
            if success:
                print(f"✅ Successfully processed {os.path.basename(json_file)}")
            else:
                print(f"❌ Failed to process {os.path.basename(json_file)}")
        except Exception as e:
            print(f"❌ Error processing {json_file}: {e}")
    
    # Check results
    from src.database.connection import DatabaseConnection
    db = DatabaseConnection()
    if db.connect():
        print(f"\n📊 Results:")
        
        # Check game types for recently processed games
        result = db.execute_query("""
            SELECT TOP 5 game_id, game_type, series_description, official_date 
            FROM games 
            WHERE game_type IS NOT NULL 
            ORDER BY game_id DESC
        """)
        
        for row in result:
            print(f"  Game {row.game_id}: {row.game_type} - {row.series_description} ({row.official_date})")
        
        db.disconnect()

if __name__ == "__main__":
    test_enhanced_loader()
