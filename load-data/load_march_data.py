#!/usr/bin/env python3
"""
Script to load all March 2025 combined data files into SQL Server database.
"""

import glob
import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from src.database.json_to_sql_loader import JSONToSQLLoader

def load_march_data():
    """Load all March 2025 combined data files to database."""
    
    # Get all combined data files from March 2025
    march_files = sorted(glob.glob('data/json/2025/03-March/combined_data_*.json'))
    total_files = len(march_files)
    
    print(f"🗂️  Found {total_files} combined data files from March 2025")
    print(f"🚀 Starting database loading process...")
    print("=" * 60)
    
    # Initialize the loader
    loader = JSONToSQLLoader()
    
    # Counters
    success_count = 0
    error_count = 0
    
    # Process each file
    for i, file_path in enumerate(march_files, 1):
        filename = os.path.basename(file_path)
        
        try:
            print(f"[{i:3d}/{total_files}] Processing {filename}...")
            
            # Load the file
            result = loader.load_json_to_database(file_path)
            
            if result:
                success_count += 1
                print(f"             ✅ Successfully loaded")
            else:
                error_count += 1
                print(f"             ❌ Failed to load")
                
        except Exception as e:
            error_count += 1
            print(f"             ❌ Error: {str(e)}")
        
        # Progress update every 50 files
        if i % 50 == 0:
            print(f"\n📊 Progress Update: {i}/{total_files} processed")
            print(f"   ✅ Success: {success_count}")
            print(f"   ❌ Errors: {error_count}")
            print(f"   📈 Success Rate: {(success_count/i)*100:.1f}%")
            print("=" * 60)
    
    # Final summary
    print(f"\n🎉 Loading Complete!")
    print(f"📊 Final Results:")
    print(f"   📁 Total files: {total_files}")
    print(f"   ✅ Successfully loaded: {success_count}")
    print(f"   ❌ Failed to load: {error_count}")
    print(f"   📈 Success rate: {(success_count/total_files)*100:.1f}%")
    
    if success_count > 0:
        print(f"\n✅ March 2025 MLB data successfully populated to SQL Server!")
        print(f"🏟️  Games loaded: {success_count}")
        print(f"📅 Date range: March 1-31, 2025")
    
    return success_count, error_count

if __name__ == "__main__":
    load_march_data()
