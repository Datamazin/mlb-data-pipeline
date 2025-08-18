#!/usr/bin/env python3
"""
Enhanced script to process all remaining boxscore files and populate missing game metadata.
This will use the enhanced loader to fetch game metadata from MLB schedule API where possible.
"""

import os
import glob
from pathlib import Path
from src.database.json_to_sql_loader import JSONToSQLLoader
from src.database.connection import DatabaseConnection

def main():
    print("🚀 Starting comprehensive game metadata population process...")
    
    # Initialize loader
    loader = JSONToSQLLoader()
    
    # Check current database status
    print("\n📊 Checking current database status...")
    db = DatabaseConnection()
    if db.connect():
        # Check game_type status
        result = db.execute_query("""
            SELECT 
                COUNT(*) as total_games,
                SUM(CASE WHEN game_type IS NOT NULL AND game_type != '' THEN 1 ELSE 0 END) as games_with_type,
                SUM(CASE WHEN series_description IS NOT NULL AND series_description != '' THEN 1 ELSE 0 END) as games_with_series,
                SUM(CASE WHEN official_date IS NOT NULL THEN 1 ELSE 0 END) as games_with_official_date,
                SUM(CASE WHEN home_team_id IS NOT NULL THEN 1 ELSE 0 END) as games_with_home_team,
                SUM(CASE WHEN away_team_id IS NOT NULL THEN 1 ELSE 0 END) as games_with_away_team
            FROM games
        """)
        
        for row in result:
            print(f"  📈 Total games: {row.total_games}")
            print(f"  🎯 Games with game_type: {row.games_with_type}/{row.total_games} ({row.games_with_type/row.total_games*100:.1f}%)")
            print(f"  📝 Games with series_description: {row.games_with_series}/{row.total_games} ({row.games_with_series/row.total_games*100:.1f}%)")
            print(f"  📅 Games with official_date: {row.games_with_official_date}/{row.total_games} ({row.games_with_official_date/row.total_games*100:.1f}%)")
            print(f"  🏠 Games with home_team_id: {row.games_with_home_team}/{row.total_games} ({row.games_with_home_team/row.total_games*100:.1f}%)")
            print(f"  ✈️ Games with away_team_id: {row.games_with_away_team}/{row.total_games} ({row.games_with_away_team/row.total_games*100:.1f}%)")
        
        db.disconnect()
    
    # Find all boxscore files
    data_dir = Path("data")
    boxscore_pattern = data_dir / "**/boxscore_raw_*.json"
    boxscore_files = list(glob.glob(str(boxscore_pattern), recursive=True))
    
    print(f"\n📁 Found {len(boxscore_files)} boxscore files to process")
    
    if len(boxscore_files) == 0:
        print("❌ No boxscore files found. Make sure data directory exists and contains boxscore_raw_*.json files")
        return
    
    # Sort files to process them in a consistent order
    boxscore_files.sort()
    
    # Process files in batches
    batch_size = 50
    total_files = len(boxscore_files)
    processed = 0
    successful = 0
    failed = 0
    
    print(f"\n🔄 Processing {total_files} files in batches of {batch_size}...")
    
    for i in range(0, total_files, batch_size):
        batch = boxscore_files[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (total_files + batch_size - 1) // batch_size
        
        print(f"\n📦 Processing batch {batch_num}/{total_batches} ({len(batch)} files)...")
        
        for file_path in batch:
            try:
                processed += 1
                file_name = os.path.basename(file_path)
                
                # Extract game ID from filename for progress tracking
                game_id = None
                if '_' in file_name:
                    parts = file_name.split('_')
                    if len(parts) >= 3:
                        game_id_part = parts[-1].replace('.json', '')
                        if game_id_part.isdigit():
                            game_id = game_id_part
                
                print(f"  🔄 [{processed:4d}/{total_files}] Processing {file_name} (Game ID: {game_id})...", end='')
                
                # Load the file using enhanced loader
                if loader.load_json_to_database(file_path):
                    successful += 1
                    print(" ✅")
                else:
                    failed += 1
                    print(" ❌")
                    
            except Exception as e:
                failed += 1
                print(f" ❌ Error: {e}")
                continue
        
        # Progress update every batch
        success_rate = (successful / processed * 100) if processed > 0 else 0
        print(f"  📊 Batch {batch_num} complete. Overall progress: {processed}/{total_files} ({success_rate:.1f}% success rate)")
    
    print(f"\n🎉 Processing complete!")
    print(f"  ✅ Successfully processed: {successful}")
    print(f"  ❌ Failed to process: {failed}")
    print(f"  📊 Success rate: {successful/total_files*100:.1f}%")
    
    # Final database status check
    print("\n📊 Final database status:")
    db = DatabaseConnection()
    if db.connect():
        result = db.execute_query("""
            SELECT 
                COUNT(*) as total_games,
                SUM(CASE WHEN game_type IS NOT NULL AND game_type != '' THEN 1 ELSE 0 END) as games_with_type,
                SUM(CASE WHEN series_description IS NOT NULL AND series_description != '' THEN 1 ELSE 0 END) as games_with_series,
                SUM(CASE WHEN official_date IS NOT NULL THEN 1 ELSE 0 END) as games_with_official_date,
                SUM(CASE WHEN home_team_id IS NOT NULL THEN 1 ELSE 0 END) as games_with_home_team,
                SUM(CASE WHEN away_team_id IS NOT NULL THEN 1 ELSE 0 END) as games_with_away_team
            FROM games
        """)
        
        for row in result:
            print(f"  📈 Total games: {row.total_games}")
            print(f"  🎯 Games with game_type: {row.games_with_type}/{row.total_games} ({row.games_with_type/row.total_games*100:.1f}%)")
            print(f"  📝 Games with series_description: {row.games_with_series}/{row.total_games} ({row.games_with_series/row.total_games*100:.1f}%)")
            print(f"  📅 Games with official_date: {row.games_with_official_date}/{row.total_games} ({row.games_with_official_date/row.total_games*100:.1f}%)")
            print(f"  🏠 Games with home_team_id: {row.games_with_home_team}/{row.total_games} ({row.games_with_home_team/row.total_games*100:.1f}%)")
            print(f"  ✈️ Games with away_team_id: {row.games_with_away_team}/{row.total_games} ({row.games_with_away_team/row.total_games*100:.1f}%)")
        
        # Show games that still need metadata
        result = db.execute_query("""
            SELECT COUNT(*) as missing_metadata
            FROM games 
            WHERE (game_type IS NULL OR game_type = '') 
               OR (series_description IS NULL OR series_description = '')
               OR official_date IS NULL
               OR home_team_id IS NULL
               OR away_team_id IS NULL
        """)
        
        for row in result:
            print(f"  ⚠️ Games still missing some metadata: {row.missing_metadata}")
        
        # Show sample of updated games
        result = db.execute_query("""
            SELECT TOP 5 game_id, game_type, series_description, home_team_id, away_team_id
            FROM games 
            WHERE game_type IS NOT NULL AND game_type != ''
            ORDER BY game_id DESC
        """)
        
        print(f"\n📝 Sample of recently updated games:")
        for row in result:
            print(f"  Game {row.game_id}: {row.game_type}, Teams: {row.home_team_id} vs {row.away_team_id}, Series: {row.series_description}")
        
        db.disconnect()
    
    print(f"\n✨ Enhanced metadata population complete!")
    print(f"   The enhanced loader automatically fetched game metadata from MLB schedule API")
    print(f"   where available and populated team IDs, game types, series descriptions, and official dates.")

if __name__ == "__main__":
    main()
