#!/usr/bin/env python3
"""
Backfill stolen bases and caught stealing statistics for existing boxscore records.

This script reads the stored raw JSON data and extracts the missing stolen base
statistics to update the boxscore table.
"""

import argparse
import json
from datetime import datetime
from src.database.connection import DatabaseConnection

def backfill_stolen_base_stats(start_date=None, end_date=None, dry_run=False):
    """
    Backfill stolen base statistics for existing boxscore records.
    
    Args:
        start_date: Start date for backfill (YYYY-MM-DD)
        end_date: End date for backfill (YYYY-MM-DD)
        dry_run: If True, only show what would be updated without making changes
    """
    db = DatabaseConnection()
    
    try:
        if not db.connect():
            print("❌ Failed to connect to database")
            return False
        
        # Build date filter
        date_filter = ""
        params = {}
        
        if start_date and end_date:
            date_filter = "WHERE g.game_date BETWEEN :start_date AND :end_date"
            params['start_date'] = start_date
            params['end_date'] = end_date
            print(f"🗓️  Backfilling stolen base stats from {start_date} to {end_date}")
        elif start_date:
            date_filter = "WHERE g.game_date >= :start_date"
            params['start_date'] = start_date
            print(f"🗓️  Backfilling stolen base stats from {start_date}")
        elif end_date:
            date_filter = "WHERE g.game_date <= :end_date"
            params['end_date'] = end_date
            print(f"🗓️  Backfilling stolen base stats up to {end_date}")
        else:
            print("🗓️  Backfilling stolen base stats for all games")
        
        # Get games that need stolen base data backfilled
        query = f"""
        SELECT DISTINCT g.game_id, g.game_date, 
               COUNT(b.id) as boxscore_records,
               COUNT(CASE WHEN b.stolen_bases IS NULL THEN 1 END) as missing_sb,
               COUNT(CASE WHEN b.caught_stealing IS NULL THEN 1 END) as missing_cs
        FROM games g
        INNER JOIN boxscore b ON g.game_id = b.game_id
        {date_filter}
        GROUP BY g.game_id, g.game_date
        HAVING COUNT(CASE WHEN b.stolen_bases IS NULL THEN 1 END) > 0
           OR COUNT(CASE WHEN b.caught_stealing IS NULL THEN 1 END) > 0
        ORDER BY g.game_date
        """
        
        result = db.execute_query(query, params)
        games_to_process = result.fetchall() if result else []
        
        if not games_to_process:
            print("✅ No games need stolen base statistics backfilled")
            return True
        
        print(f"📊 Found {len(games_to_process)} games needing stolen base backfill")
        
        total_updated = 0
        total_processed = 0
        total_errors = 0
        
        for game_id, game_date, boxscore_records, missing_sb, missing_cs in games_to_process:
            try:
                print(f"\n🎮 Processing game {game_id} ({game_date})")
                print(f"   📈 {boxscore_records} boxscore records, {missing_sb} missing stolen bases, {missing_cs} missing caught stealing")
                
                # Get the raw JSON data for this game
                json_query = """
                SELECT json_data 
                FROM raw_json_data 
                WHERE game_id = :game_id 
                AND data_type IN ('combined', 'boxscore')
                ORDER BY extraction_timestamp DESC
                """
                
                json_result = db.execute_query(json_query, {'game_id': game_id})
                json_rows = json_result.fetchall() if json_result else []
                
                if not json_rows:
                    print(f"   ⚠️  No raw JSON data found for game {game_id}")
                    continue
                
                # Parse the JSON data
                json_data_str = json_rows[0][0]  # Get the first (most recent) JSON data
                try:
                    game_data = json.loads(json_data_str)
                except json.JSONDecodeError as e:
                    print(f"   ❌ Error parsing JSON for game {game_id}: {e}")
                    total_errors += 1
                    continue
                
                # Extract boxscore data
                boxscore_data = game_data.get('boxscore', {})
                if not boxscore_data:
                    print(f"   ⚠️  No boxscore data found in JSON for game {game_id}")
                    continue
                
                # Process players from both teams
                teams = boxscore_data.get('teams', {})
                updates_made = 0
                
                for team_type in ['home', 'away']:
                    team_data = teams.get(team_type, {})
                    players = team_data.get('players', {})
                    
                    for player_key, player_data in players.items():
                        if player_key.startswith('ID'):
                            person = player_data.get('person', {})
                            stats = player_data.get('stats', {})
                            batting = stats.get('batting', {})
                            
                            if batting and person.get('id'):
                                player_id = person.get('id')
                                stolen_bases = batting.get('stolenBases', 0)
                                caught_stealing = batting.get('caughtStealing', 0)
                                base_on_balls = batting.get('baseOnBalls', 0)  # Also fix walks
                                
                                if dry_run:
                                    print(f"   👤 Player {player_id}: SB={stolen_bases}, CS={caught_stealing}, BB={base_on_balls}")
                                else:
                                    # Update the boxscore record
                                    update_query = """
                                    UPDATE boxscore 
                                    SET stolen_bases = :stolen_bases,
                                        caught_stealing = :caught_stealing,
                                        walks = :walks
                                    WHERE game_id = :game_id 
                                    AND player_id = :player_id
                                    """
                                    
                                    update_params = {
                                        'stolen_bases': stolen_bases,
                                        'caught_stealing': caught_stealing,
                                        'walks': base_on_balls,
                                        'game_id': game_id,
                                        'player_id': player_id
                                    }
                                    
                                    update_result = db.execute_query(update_query, update_params)
                                    if update_result and update_result.rowcount > 0:
                                        updates_made += 1
                                        total_updated += 1
                
                total_processed += 1
                
                if not dry_run and updates_made > 0:
                    print(f"   ✅ Updated {updates_made} player records")
                elif not dry_run:
                    print(f"   ℹ️  No updates needed")
                
            except Exception as e:
                print(f"   ❌ Error processing game {game_id}: {e}")
                total_errors += 1
                continue
        
        print(f"\n🎉 Backfill completed!")
        print(f"   📊 Processed: {total_processed} games")
        print(f"   ✅ Updated: {total_updated} player records")
        print(f"   ❌ Errors: {total_errors}")
        
        if dry_run:
            print("\n💡 This was a dry run. Use --execute to apply changes.")
        
        return total_errors == 0
        
    except Exception as e:
        print(f"❌ Error during backfill: {e}")
        return False
    finally:
        db.disconnect()

def main():
    parser = argparse.ArgumentParser(description='Backfill stolen base statistics')
    parser.add_argument('--start', type=str, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', type=str, help='End date (YYYY-MM-DD)')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be updated without making changes')
    parser.add_argument('--execute', action='store_true',
                       help='Actually execute the updates')
    
    args = parser.parse_args()
    
    if not args.dry_run and not args.execute:
        print("❌ Must specify either --dry-run or --execute")
        return False
    
    dry_run = args.dry_run
    
    # Validate dates
    start_date = None
    end_date = None
    
    if args.start:
        try:
            datetime.strptime(args.start, '%Y-%m-%d')
            start_date = args.start
        except ValueError:
            print(f"❌ Invalid start date format: {args.start}. Use YYYY-MM-DD")
            return False
    
    if args.end:
        try:
            datetime.strptime(args.end, '%Y-%m-%d')
            end_date = args.end
        except ValueError:
            print(f"❌ Invalid end date format: {args.end}. Use YYYY-MM-DD")
            return False
    
    return backfill_stolen_base_stats(start_date, end_date, dry_run)

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
