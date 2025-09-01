#!/usr/bin/env python3
"""
Repopulate Missing Batting Statistics (Walks, Stolen Bases, Caught Stealing)

This script fixes missing batting statistics by re-processing existing JSON data
and updating the database with the correct values for:
- Base on Balls (Walks)
- Stolen Bases
- Caught Stealing

The script can work in different modes:
1. Fix all data in the database
2. Fix data for a specific date range
3. Fix data for specific games
4. Dry-run mode to preview changes
"""

import os
import sys
import json
import argparse
from datetime import datetime, date, timedelta
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database.connection import DatabaseConnection
from utils.json_handler import load_from_json

class BattingStatsRepopulator:
    def __init__(self):
        self.db = DatabaseConnection()
        self.stats_updated = 0
        self.errors = 0
        
    def get_games_with_missing_stats(self, start_date=None, end_date=None):
        """Get games that have missing or zero batting statistics."""
        base_query = """
        SELECT DISTINCT g.game_id, g.game_date, g.home_team_id, g.away_team_id,
               COUNT(b.id) as boxscore_count,
               SUM(CASE WHEN b.walks IS NULL OR b.walks = 0 THEN 1 ELSE 0 END) as missing_walks,
               SUM(CASE WHEN b.stolen_bases IS NULL THEN 1 ELSE 0 END) as missing_stolen_bases,
               SUM(CASE WHEN b.caught_stealing IS NULL THEN 1 ELSE 0 END) as missing_caught_stealing,
               SUM(ISNULL(b.walks, 0)) as total_walks,
               SUM(ISNULL(b.stolen_bases, 0)) as total_stolen_bases,
               SUM(ISNULL(b.caught_stealing, 0)) as total_caught_stealing
        FROM games g
        LEFT JOIN boxscore b ON g.game_id = b.game_id
        """
        
        params = {}
        
        if start_date and end_date:
            base_query += " WHERE g.game_date >= :start_date AND g.game_date <= :end_date"
            params['start_date'] = start_date
            params['end_date'] = end_date
        elif start_date:
            base_query += " WHERE g.game_date >= :start_date"
            params['start_date'] = start_date
        elif end_date:
            base_query += " WHERE g.game_date <= :end_date"
            params['end_date'] = end_date
            
        base_query += """
        GROUP BY g.game_id, g.game_date, g.home_team_id, g.away_team_id
        HAVING COUNT(b.id) > 0
        ORDER BY g.game_date DESC, g.game_id
        """
        
        return self.db.fetch_results(base_query, params)
    
    def find_json_file_for_game(self, game_id, game_date):
        """Find the JSON file containing data for a specific game."""
        # Try different possible locations
        possible_paths = [
            Path(f"data/json/{game_date.year}/{game_date.strftime('%m-%B')}/combined_data_{game_id}_{game_date.strftime('%Y%m%d')}.json"),
            Path(f"data/json/{game_date.year}/{game_date.strftime('%m-%B')}/boxscore_raw_{game_id}.json"),
            Path(f"data/raw/{game_date.year}/{game_date.strftime('%m-%B')}/combined_data_{game_id}_{game_date.strftime('%Y%m%d')}.json"),
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
                
        return None
    
    def extract_batting_stats_from_json(self, json_data, game_id):
        """Extract batting statistics from JSON data."""
        batting_updates = []
        
        try:
            # Handle different JSON structures
            if 'boxscore' in json_data:
                boxscore_data = json_data['boxscore']
            elif 'teams' in json_data:
                boxscore_data = json_data
            else:
                boxscore_data = json_data
            
            # Process both teams
            if 'teams' in boxscore_data:
                for team_key in ['away', 'home']:
                    if team_key in boxscore_data['teams']:
                        team_data = boxscore_data['teams'][team_key]
                        
                        if 'players' in team_data:
                            for player_id, player_data in team_data['players'].items():
                                if player_id.startswith('ID'):
                                    actual_player_id = player_id.replace('ID', '')
                                    
                                    # Extract batting stats
                                    if 'stats' in player_data and 'batting' in player_data['stats']:
                                        batting_stats = player_data['stats']['batting']
                                        
                                        # Extract the enhanced statistics
                                        walks = batting_stats.get('baseOnBalls', 0)
                                        stolen_bases = batting_stats.get('stolenBases', 0)
                                        caught_stealing = batting_stats.get('caughtStealing', 0)
                                        
                                        # Only include if player has meaningful stats
                                        plate_appearances = batting_stats.get('plateAppearances', 0)
                                        at_bats = batting_stats.get('atBats', 0)
                                        
                                        if plate_appearances > 0 or at_bats > 0:
                                            batting_updates.append({
                                                'player_id': int(actual_player_id),
                                                'game_id': game_id,
                                                'walks': walks,
                                                'stolen_bases': stolen_bases,
                                                'caught_stealing': caught_stealing,
                                                'plate_appearances': plate_appearances,
                                                'at_bats': at_bats
                                            })
            
            return batting_updates
            
        except Exception as e:
            print(f"   ❌ Error extracting batting stats from JSON: {e}")
            return []
    
    def update_batting_stats_in_database(self, batting_updates, dry_run=False):
        """Update batting statistics in the database."""
        if not batting_updates:
            return 0
            
        updated_count = 0
        
        for update in batting_updates:
            try:
                if dry_run:
                    print(f"   Would update player {update['player_id']} game {update['game_id']}: "
                          f"walks={update['walks']}, SB={update['stolen_bases']}, CS={update['caught_stealing']}")
                    updated_count += 1
                else:
                    # Update the boxscore record
                    update_query = """
                    UPDATE boxscore 
                    SET walks = :walks,
                        stolen_bases = :stolen_bases,
                        caught_stealing = :caught_stealing
                    WHERE player_id = :player_id AND game_id = :game_id
                    """
                    
                    result = self.db.execute_query(update_query, {
                        'walks': update['walks'],
                        'stolen_bases': update['stolen_bases'],
                        'caught_stealing': update['caught_stealing'],
                        'player_id': update['player_id'],
                        'game_id': update['game_id']
                    })
                    
                    if result:
                        updated_count += 1
                    
            except Exception as e:
                print(f"   ❌ Error updating player {update['player_id']}: {e}")
                self.errors += 1
        
        return updated_count
    
    def repopulate_game_stats(self, game_id, game_date, dry_run=False):
        """Repopulate batting stats for a single game."""
        print(f"   🔄 Processing game {game_id} ({game_date})...")
        
        # Find JSON file for this game
        json_file = self.find_json_file_for_game(game_id, game_date)
        
        if not json_file:
            print(f"   ⚠️  No JSON file found for game {game_id}")
            return 0
            
        # Load JSON data
        try:
            json_data = load_from_json(str(json_file))
            if not json_data:
                print(f"   ❌ Failed to load JSON data from {json_file}")
                return 0
        except Exception as e:
            print(f"   ❌ Error loading JSON file {json_file}: {e}")
            return 0
        
        # Extract batting statistics
        batting_updates = self.extract_batting_stats_from_json(json_data, game_id)
        
        if not batting_updates:
            print(f"   ⚠️  No batting statistics found in JSON for game {game_id}")
            return 0
            
        print(f"   📊 Found batting stats for {len(batting_updates)} players")
        
        # Update database
        updated_count = self.update_batting_stats_in_database(batting_updates, dry_run)
        
        if not dry_run:
            print(f"   ✅ Updated {updated_count} player records")
        else:
            print(f"   🔍 Would update {updated_count} player records")
            
        return updated_count
    
    def repopulate_stats_for_date_range(self, start_date=None, end_date=None, dry_run=False):
        """Repopulate batting stats for a date range."""
        print(f"🔄 REPOPULATING BATTING STATISTICS")
        print("=" * 60)
        
        if start_date and end_date:
            print(f"📅 Date range: {start_date} to {end_date}")
        elif start_date:
            print(f"📅 From date: {start_date}")
        elif end_date:
            print(f"📅 To date: {end_date}")
        else:
            print(f"📅 All games in database")
            
        if dry_run:
            print("🔍 DRY RUN MODE - No data will be modified")
        
        print("=" * 60)
        
        # Connect to database
        if not self.db.connect():
            print("❌ Failed to connect to database")
            return False
            
        try:
            # Get games that need stats updates
            print("1. Analyzing games with missing batting statistics...")
            games_data = self.get_games_with_missing_stats(start_date, end_date)
            
            if not games_data:
                print("   ✅ No games found to update")
                return True
                
            print(f"   📊 Found {len(games_data)} games to analyze")
            
            # Show summary of missing stats
            total_missing_walks = sum(row[5] for row in games_data)  # missing_walks
            total_missing_sb = sum(row[6] for row in games_data)     # missing_stolen_bases
            total_missing_cs = sum(row[7] for row in games_data)     # missing_caught_stealing
            
            print(f"   Missing statistics summary:")
            print(f"     Records missing walks: {total_missing_walks}")
            print(f"     Records missing stolen bases: {total_missing_sb}")
            print(f"     Records missing caught stealing: {total_missing_cs}")
            
            # Process each game
            print(f"\n2. Repopulating statistics for {len(games_data)} games...")
            
            total_updated = 0
            games_processed = 0
            games_with_json = 0
            
            for i, (game_id, game_date, home_team, away_team, boxscore_count, 
                   missing_walks, missing_sb, missing_cs, total_walks, total_sb, total_cs) in enumerate(games_data, 1):
                
                print(f"\n   [{i}/{len(games_data)}] Game {game_id} ({game_date})")
                print(f"     Current stats: {total_walks} walks, {total_sb} SB, {total_cs} CS")
                print(f"     Missing records: {missing_walks} walks, {missing_sb} SB, {missing_cs} CS")
                
                updated_count = self.repopulate_game_stats(game_id, game_date, dry_run)
                
                if updated_count > 0:
                    total_updated += updated_count
                    games_with_json += 1
                    
                games_processed += 1
                
                # Progress update every 10 games
                if i % 10 == 0:
                    print(f"\n   📈 Progress: {i}/{len(games_data)} games processed")
                    print(f"      Updated {total_updated} player records so far")
            
            print(f"\n3. Repopulation completed!")
            print(f"   ✅ Games processed: {games_processed}")
            print(f"   📁 Games with JSON files: {games_with_json}")
            print(f"   🔄 Player records updated: {total_updated}")
            print(f"   ❌ Errors encountered: {self.errors}")
            
            if not dry_run and total_updated > 0:
                # Verify the updates
                print(f"\n4. Verifying updated statistics...")
                
                verification_query = """
                SELECT 
                    SUM(CASE WHEN b.walks > 0 THEN 1 ELSE 0 END) as records_with_walks,
                    SUM(CASE WHEN b.stolen_bases > 0 THEN 1 ELSE 0 END) as records_with_sb,
                    SUM(CASE WHEN b.caught_stealing > 0 THEN 1 ELSE 0 END) as records_with_cs,
                    SUM(ISNULL(b.walks, 0)) as total_walks,
                    SUM(ISNULL(b.stolen_bases, 0)) as total_sb,
                    SUM(ISNULL(b.caught_stealing, 0)) as total_cs,
                    COUNT(*) as total_records
                FROM boxscore b
                INNER JOIN games g ON b.game_id = g.game_id
                """
                
                params = {}
                if start_date and end_date:
                    verification_query += " WHERE g.game_date >= :start_date AND g.game_date <= :end_date"
                    params['start_date'] = start_date
                    params['end_date'] = end_date
                elif start_date:
                    verification_query += " WHERE g.game_date >= :start_date"
                    params['start_date'] = start_date
                elif end_date:
                    verification_query += " WHERE g.game_date <= :end_date"
                    params['end_date'] = end_date
                
                stats = self.db.fetch_results(verification_query, params)[0]
                
                print(f"   📊 Updated statistics:")
                print(f"     Records with walks: {stats[0]} (Total walks: {stats[3]})")
                print(f"     Records with stolen bases: {stats[1]} (Total SB: {stats[4]})")
                print(f"     Records with caught stealing: {stats[2]} (Total CS: {stats[5]})")
                print(f"     Total boxscore records: {stats[6]}")
                
                if stats[3] > 0 or stats[4] > 0 or stats[5] > 0:
                    print(f"   ✅ Enhanced batting statistics successfully updated!")
                else:
                    print(f"   ⚠️  All statistics are still zero - check JSON data")
            
            return total_updated > 0
            
        except Exception as e:
            print(f"❌ Error during repopulation: {e}")
            import traceback
            traceback.print_exc()
            return False
            
        finally:
            self.db.disconnect()
    
    def repopulate_specific_games(self, game_ids, dry_run=False):
        """Repopulate batting stats for specific games."""
        print(f"🔄 REPOPULATING BATTING STATISTICS FOR SPECIFIC GAMES")
        print("=" * 60)
        print(f"📊 Games to process: {', '.join(map(str, game_ids))}")
        
        if dry_run:
            print("🔍 DRY RUN MODE - No data will be modified")
        
        print("=" * 60)
        
        # Connect to database
        if not self.db.connect():
            print("❌ Failed to connect to database")
            return False
            
        try:
            total_updated = 0
            
            for i, game_id in enumerate(game_ids, 1):
                print(f"\n[{i}/{len(game_ids)}] Processing game {game_id}...")
                
                # Get game date
                game_info = self.db.fetch_results("""
                SELECT game_date FROM games WHERE game_id = :game_id
                """, {"game_id": game_id})
                
                if not game_info:
                    print(f"   ❌ Game {game_id} not found in database")
                    continue
                    
                game_date = game_info[0][0]
                updated_count = self.repopulate_game_stats(game_id, game_date, dry_run)
                total_updated += updated_count
            
            print(f"\n✅ Completed processing {len(game_ids)} games")
            print(f"🔄 Total player records updated: {total_updated}")
            
            return total_updated > 0
            
        except Exception as e:
            print(f"❌ Error processing specific games: {e}")
            return False
            
        finally:
            self.db.disconnect()

def parse_date(date_str):
    """Parse date string in various formats."""
    formats = ['%Y-%m-%d', '%m/%d/%Y', '%m-%d-%Y', '%Y%m%d']
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    
    raise ValueError(f"Unable to parse date '{date_str}'. Use format YYYY-MM-DD")

def main():
    """Main function with command line argument parsing."""
    parser = argparse.ArgumentParser(
        description="Repopulate missing batting statistics (walks, stolen bases, caught stealing)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fix batting stats for today
  python repopulate_batting_stats.py --start 2025-08-31 --end 2025-08-31

  # Fix all batting stats in database (be careful!)
  python repopulate_batting_stats.py --all

  # Fix batting stats for August 2025
  python repopulate_batting_stats.py --start 2025-08-01 --end 2025-08-31

  # Dry run to see what would be updated
  python repopulate_batting_stats.py --start 2025-08-31 --end 2025-08-31 --dry-run

  # Fix specific games
  python repopulate_batting_stats.py --games 776510 776512 776513
  
  # Fix last 7 days
  python repopulate_batting_stats.py --last-days 7
        """
    )
    
    # Date range options
    date_group = parser.add_mutually_exclusive_group()
    date_group.add_argument(
        '--start', 
        help='Start date (YYYY-MM-DD format)'
    )
    
    parser.add_argument(
        '--end', 
        help='End date (YYYY-MM-DD format, used with --start)'
    )
    
    date_group.add_argument(
        '--all', 
        action='store_true',
        help='Repopulate all games in database (use with caution!)'
    )
    
    date_group.add_argument(
        '--last-days', 
        type=int,
        help='Repopulate last N days of data'
    )
    
    date_group.add_argument(
        '--games', 
        nargs='+',
        type=int,
        help='Specific game IDs to repopulate'
    )
    
    parser.add_argument(
        '--dry-run', 
        action='store_true',
        help='Show what would be updated without making changes'
    )
    
    args = parser.parse_args()
    
    # Create repopulator
    repopulator = BattingStatsRepopulator()
    
    try:
        if args.games:
            # Repopulate specific games
            success = repopulator.repopulate_specific_games(args.games, dry_run=args.dry_run)
            
        elif args.all:
            # Repopulate all games
            print("⚠️  WARNING: This will repopulate ALL games in the database!")
            if not args.dry_run:
                response = input("Are you sure you want to continue? (y/N): ").strip().lower()
                if response != 'y':
                    print("Operation cancelled")
                    sys.exit(0)
            
            success = repopulator.repopulate_stats_for_date_range(dry_run=args.dry_run)
            
        elif args.last_days:
            # Repopulate last N days
            end_date = date.today()
            start_date = end_date - timedelta(days=args.last_days - 1)
            
            print(f"📅 Repopulating last {args.last_days} days: {start_date} to {end_date}")
            success = repopulator.repopulate_stats_for_date_range(start_date, end_date, dry_run=args.dry_run)
            
        elif args.start:
            # Date range specified
            start_date = parse_date(args.start)
            end_date = parse_date(args.end) if args.end else start_date
            
            if start_date > end_date:
                print("❌ Error: Start date must be before or equal to end date")
                sys.exit(1)
            
            success = repopulator.repopulate_stats_for_date_range(start_date, end_date, dry_run=args.dry_run)
            
        else:
            # Default: repopulate today's data
            today = date.today()
            print(f"📅 No date range specified - defaulting to today: {today}")
            success = repopulator.repopulate_stats_for_date_range(today, today, dry_run=args.dry_run)
        
        if success:
            if args.dry_run:
                print(f"\n🔍 Dry run completed - no changes made")
                print(f"💡 Remove --dry-run to apply the updates")
            else:
                print(f"\n🎉 Batting statistics repopulation completed!")
                print(f"✅ Updated {repopulator.stats_updated} player records")
                if repopulator.errors > 0:
                    print(f"⚠️  {repopulator.errors} errors encountered")
        else:
            print(f"\n❌ Repopulation failed or no updates needed")
            
    except ValueError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n⚠️  Operation cancelled by user")
        sys.exit(0)

if __name__ == "__main__":
    main()
