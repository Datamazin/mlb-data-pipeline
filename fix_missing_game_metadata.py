#!/usr/bin/env python3
"""
Fix Missing Game Metadata for March and April 2025

This script fixes the missing game_type, series_description, and official_date
fields for games loaded before the metadata API integration was working properly.
"""

import os
import sys
from datetime import datetime, date

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database.connection import DatabaseConnection
from api.mlb_client import MLBClient

def fix_missing_game_metadata(start_date, end_date, dry_run=False):
    """Fix missing metadata for games in the specified date range."""
    
    print(f"🔧 FIXING MISSING GAME METADATA: {start_date} to {end_date}")
    print("=" * 70)
    
    if dry_run:
        print("🔍 DRY RUN MODE - No data will be modified")
        print("=" * 70)
    
    # Initialize connections
    db = DatabaseConnection()
    mlb_client = MLBClient()
    
    try:
        if not dry_run:
            db.connect()
        
        # 1. Find games with missing metadata in the date range
        print(f"1. Finding games with missing metadata for {start_date} to {end_date}...")
        
        if not dry_run:
            missing_metadata_games = db.fetch_results("""
            SELECT game_id, game_date, home_team_id, away_team_id
            FROM games 
            WHERE game_date >= :start_date AND game_date <= :end_date
              AND (game_type IS NULL OR series_description IS NULL OR official_date IS NULL)
            ORDER BY game_date, game_id
            """, {"start_date": start_date, "end_date": end_date})
            
            print(f"   Found {len(missing_metadata_games)} games with missing metadata")
            
            if len(missing_metadata_games) == 0:
                print("✅ No games found with missing metadata!")
                return
            
            # Show sample of missing games
            print("   Sample games with missing metadata:")
            for i, (game_id, game_date, home_id, away_id) in enumerate(missing_metadata_games[:5], 1):
                print(f"     {i}. Game {game_id} on {game_date}")
            if len(missing_metadata_games) > 5:
                print(f"     ... and {len(missing_metadata_games) - 5} more")
        else:
            print("   (Skipped in dry run mode)")
            return
        
        # 2. Fetch and update metadata for each game
        print(f"\n2. Fetching metadata from MLB API for {len(missing_metadata_games)} games...")
        
        success_count = 0
        error_count = 0
        api_failures = 0
        
        for i, (game_id, game_date, home_id, away_id) in enumerate(missing_metadata_games, 1):
            try:
                print(f"   [{i}/{len(missing_metadata_games)}] Fetching metadata for game {game_id} ({game_date})...")
                
                # Fetch game metadata from MLB API
                metadata = mlb_client.fetch_game_metadata(game_id)
                
                if metadata:
                    # Update the game with the fetched metadata
                    update_query = """
                    UPDATE games SET 
                        game_type = :game_type,
                        series_description = :series_description,
                        official_date = :official_date
                    WHERE game_id = :game_id
                    """
                    update_params = {
                        'game_id': game_id,
                        'game_type': metadata.get('game_type'),
                        'series_description': metadata.get('series_description'),
                        'official_date': metadata.get('official_date')
                    }
                    
                    db.execute_query(update_query, update_params)
                    success_count += 1
                    
                    print(f"     ✅ Updated: type={metadata.get('game_type')}, series={metadata.get('series_description')}")
                else:
                    print(f"     ⚠️ No metadata found for game {game_id}")
                    api_failures += 1
                
                # Progress update every 50 games
                if i % 50 == 0:
                    print(f"   Progress: {i}/{len(missing_metadata_games)} games processed")
                
            except Exception as e:
                print(f"   ❌ Error updating game {game_id}: {e}")
                error_count += 1
        
        print(f"\n3. Metadata update completed!")
        print(f"   ✅ Successfully updated: {success_count} games")
        print(f"   ⚠️ API failures: {api_failures} games (no metadata available)")
        print(f"   ❌ Errors: {error_count} games")
        
        # 4. Verify the fixes
        print(f"\n4. Verifying metadata fixes for {start_date} to {end_date}...")
        
        # Check updated field population
        verification_results = db.fetch_results("""
        SELECT 
            COUNT(*) as total_games,
            COUNT(game_type) as game_type_populated,
            COUNT(series_description) as series_description_populated,
            COUNT(official_date) as official_date_populated,
            COUNT(CASE WHEN game_type IS NULL THEN 1 END) as game_type_nulls,
            COUNT(CASE WHEN series_description IS NULL THEN 1 END) as series_description_nulls,
            COUNT(CASE WHEN official_date IS NULL THEN 1 END) as official_date_nulls
        FROM games 
        WHERE game_date >= :start_date AND game_date <= :end_date
        """, {"start_date": start_date, "end_date": end_date})[0]
        
        total, gt_pop, sd_pop, od_pop, gt_null, sd_null, od_null = verification_results
        
        print(f"   Total games in range: {total}")
        print(f"   game_type populated: {gt_pop} ({gt_null} still NULL)")
        print(f"   series_description populated: {sd_pop} ({sd_null} still NULL)")
        print(f"   official_date populated: {od_pop} ({od_null} still NULL)")
        
        if gt_null == 0 and sd_null == 0 and od_null == 0:
            print(f"   🎉 All metadata fields successfully populated!")
        else:
            print(f"   ⚠️ Some games still have NULL metadata (likely API limitations)")
        
        # Show sample of updated games
        sample_games = db.fetch_results("""
        SELECT TOP 3
            game_id, game_date, game_type, series_description, official_date
        FROM games 
        WHERE game_date >= :start_date AND game_date <= :end_date
          AND game_type IS NOT NULL
        ORDER BY game_date
        """, {"start_date": start_date, "end_date": end_date})
        
        if sample_games:
            print(f"\n   Sample updated games:")
            for game_id, game_date, game_type, series_desc, official_date in sample_games:
                print(f"     Game {game_id} ({game_date}): {game_type}, {series_desc}")
        
        print(f"\n✅ Metadata fix completed!")
        
    except Exception as e:
        print(f"❌ Error fixing metadata: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if not dry_run:
            db.disconnect()

def main():
    """Main function to fix missing metadata."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Fix missing game metadata for specified date range",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fix March and April 2025 metadata
  python fix_missing_game_metadata.py --start 2025-03-01 --end 2025-04-30

  # Dry run to see what would be fixed
  python fix_missing_game_metadata.py --start 2025-03-01 --end 2025-04-30 --dry-run
        """
    )
    
    parser.add_argument(
        '--start', 
        required=True,
        help='Start date (YYYY-MM-DD format)'
    )
    
    parser.add_argument(
        '--end', 
        required=True,
        help='End date (YYYY-MM-DD format)'
    )
    
    parser.add_argument(
        '--dry-run', 
        action='store_true',
        help='Show what would be fixed without actually updating data'
    )
    
    args = parser.parse_args()
    
    try:
        from datetime import datetime
        start_date = datetime.strptime(args.start, '%Y-%m-%d').date()
        end_date = datetime.strptime(args.end, '%Y-%m-%d').date()
        
        if start_date > end_date:
            print("❌ Error: Start date must be before or equal to end date")
            sys.exit(1)
        
        fix_missing_game_metadata(
            start_date=start_date,
            end_date=end_date,
            dry_run=args.dry_run
        )
        
    except ValueError as e:
        print(f"❌ Error parsing dates: {e}")
        print("Use format YYYY-MM-DD")
        sys.exit(1)

if __name__ == "__main__":
    main()
