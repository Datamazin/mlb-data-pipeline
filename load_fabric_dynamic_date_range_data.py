#!/usr/bin/env python3
"""
Load MLB Data for Dynamic Date Range with Enhanced Batting Statistics and Auto-Extraction

This script provides a complete end-to-end solution for loading MLB data:
1. Automatically creates missing month folders
2. Automatically extracts missing data when no files exist
3. Loads data incrementally (only missing dates by default)
4. Enhanced batting statistics validation

Features:
- Dynamic date range processing
- Automatic folder creation for new months
- Automatic data extraction when needed
- Incremental loading (skip existing dates)
- Enhanced batting statistics (doubles, triples, home runs)
- Comprehensive error handling and reporting
- Dry-run mode for preview
"""

import os
import sys
import glob
import argparse
from datetime import datetime, date, timedelta
from pathlib import Path
import time

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database.connection import DatabaseConnection
from database.json_to_sql_loader import JSONToSQLLoader
from etl.extract import extract_season_data, get_games_for_date
from api.mlb_client import MLBClient
from utils.json_handler import save_raw_api_data, save_to_json

def extract_date_from_filename(filename):
    """Extract date from combined_data_*.json filename."""
    import re
    # Look for date pattern in filename (e.g., combined_data_777123_20250615.json)
    date_match = re.search(r'_(\d{8})\.json$', filename)
    if date_match:
        date_str = date_match.group(1)
        try:
            return datetime.strptime(date_str, '%Y%m%d').date()
        except ValueError:
            pass
    return None

def parse_date(date_str):
    """Parse date string in various formats."""
    formats = ['%Y-%m-%d', '%m/%d/%Y', '%m-%d-%Y', '%Y%m%d']
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    
    raise ValueError(f"Unable to parse date '{date_str}'. Use format YYYY-MM-DD")

def get_date_folders(start_date, end_date, base_path="data/json", create_missing=True):
    """Get all date folders that fall within the specified range.
    
    Args:
        start_date: Start date for the range
        end_date: End date for the range  
        base_path: Base path to search for date folders
        create_missing: If True, creates missing month folders
    
    Returns:
        List of Path objects for date folders in range
    """
    base_path = Path(base_path)
    folders = []
    missing_folders = []
    
    # Generate expected folders for the date range
    current_date = start_date.replace(day=1)  # Start of month
    end_month = end_date.replace(day=1)  # Start of end month
    
    while current_date <= end_month:
        year = current_date.year
        month = current_date.month
        
        # Create expected folder path
        year_folder = base_path / str(year)
        month_name = current_date.strftime("%m-%B")  # e.g., "08-August"
        month_folder = year_folder / month_name
        
        if month_folder.exists():
            folders.append(month_folder)
        else:
            missing_folders.append((month_folder, current_date))
        
        # Move to next month
        if month == 12:
            current_date = current_date.replace(year=year + 1, month=1)
        else:
            current_date = current_date.replace(month=month + 1)
    
    # Create missing folders if requested
    if create_missing and missing_folders:
        print(f"   📁 Creating missing month folders:")
        for folder_path, folder_date in missing_folders:
            try:
                folder_path.mkdir(parents=True, exist_ok=True)
                print(f"     ✅ Created: {folder_path}")
                folders.append(folder_path)
            except Exception as e:
                print(f"     ❌ Failed to create {folder_path}: {e}")
    
    return sorted(folders)

def extract_missing_data(start_date, end_date, dry_run=False):
    """Extract missing MLB data for the specified date range.
    
    Args:
        start_date: Start date for extraction
        end_date: End date for extraction  
        dry_run: If True, show what would be extracted without actually doing it
        
    Returns:
        Dictionary with extraction statistics
    """
    print(f"\n🔍 EXTRACTING MISSING DATA FOR: {start_date} to {end_date}")
    print("=" * 70)
    
    if dry_run:
        print("🔍 DRY RUN MODE - No data will be extracted")
        print("=" * 70)
        
        # Just show what dates we would process
        current_date = start_date
        dates_to_process = []
        
        while current_date <= end_date:
            dates_to_process.append(current_date)
            current_date += timedelta(days=1)
        
        print(f"Would extract data for {len(dates_to_process)} dates:")
        for i, process_date in enumerate(dates_to_process[:10], 1):
            print(f"   {i}. {process_date}")
        if len(dates_to_process) > 10:
            print(f"   ... and {len(dates_to_process) - 10} more dates")
            
        return {
            'total_days': len(dates_to_process),
            'dry_run': True
        }
    
    # Use the existing extract_season_data function
    print("🚀 Starting data extraction...")
    
    try:
        stats = extract_season_data(
            year=start_date.year,
            start_date=start_date,
            end_date=end_date,
            save_json=True,
            delay_seconds=1  # Be respectful to MLB API
        )
        
        print(f"\n✅ EXTRACTION COMPLETED!")
        print(f"   📊 Extracted {stats['games_extracted']} games")
        print(f"   📁 Saved {stats['json_files_saved']} JSON files")
        print(f"   ⏱️  Duration: {stats['total_duration']}")
        
        if stats['games_failed'] > 0:
            print(f"   ⚠️  {stats['games_failed']} games failed to extract")
        
        return stats
        
    except Exception as e:
        print(f"❌ Error during extraction: {e}")
        import traceback
        traceback.print_exc()
        return {'error': str(e)}

def load_dynamic_date_range_data(start_date, end_date, clear_existing=False, dry_run=False, create_folders=True, auto_extract=True):
    """Load MLB data for a dynamic date range with enhanced batting statistics.
    
    By default, only loads data for dates that don't already exist in the database.
    Use --clear to force reload all data in the range.
    If no data files exist for the date range, automatically extracts them first.
    
    Args:
        start_date: Start date for loading
        end_date: End date for loading
        clear_existing: If True, clear existing data before loading
        dry_run: If True, show what would be done without making changes
        create_folders: If True, automatically create missing month folders
        auto_extract: If True, automatically extract missing data when needed
    """
    
    print(f"🚀 LOADING DATA FOR DATE RANGE: {start_date} to {end_date}")
    print("=" * 70)
    
    if dry_run:
        print("🔍 DRY RUN MODE - No data will be modified")
        print("=" * 70)
    
    # Initialize database connection
    db = DatabaseConnection()
    
    try:
        if not dry_run:
            db.connect()
        
        # 1. Check existing data in the date range
        print(f"1. Analyzing existing data for {start_date} to {end_date}...")
        
        if not dry_run:
            existing_count = db.fetch_results("""
            SELECT COUNT(*) as count
            FROM games 
            WHERE game_date >= :start_date AND game_date <= :end_date
            """, {"start_date": start_date, "end_date": end_date})[0][0]
            
            print(f"   Found {existing_count} existing games in date range")
            
            if clear_existing and existing_count > 0:
                print("   🗑️  Clearing existing data to reload with enhanced stats...")
                
                # Use transaction to clear data safely
                delete_queries = [
                    f"""
                    DELETE FROM boxscore 
                    WHERE game_id IN (
                        SELECT game_id FROM games 
                        WHERE game_date >= '{start_date}' AND game_date <= '{end_date}'
                    )
                    """,
                    f"""
                    DELETE FROM games 
                    WHERE game_date >= '{start_date}' AND game_date <= '{end_date}'
                    """
                ]
                
                db.execute_transaction(delete_queries)
                print("   ✅ Existing data cleared")
                existing_dates = set()  # No existing dates after clearing
            else:
                # Get list of dates that already exist in database
                existing_dates_result = db.fetch_results("""
                SELECT DISTINCT game_date
                FROM games 
                WHERE game_date >= :start_date AND game_date <= :end_date
                """, {"start_date": start_date, "end_date": end_date})
                
                existing_dates = {row[0] for row in existing_dates_result}
                
                if existing_dates:
                    print(f"   📅 Found data for {len(existing_dates)} dates already in database")
                    if not clear_existing:
                        print("   🔄 Will only load missing dates (incremental loading)")
                        print("   💡 Use --clear to force reload all data")
                else:
                    print("   📂 No existing data found - will load all files")
        else:
            print("   (Skipped in dry run mode)")
            existing_dates = set()
        
        # 2. Find all data folders for the date range (and create missing ones)
        print(f"\n2. Scanning for data folders in date range...")
        date_folders = get_date_folders(start_date, end_date, create_missing=create_folders)
        
        print(f"   Found/Created {len(date_folders)} date folders:")
        for folder in date_folders:
            print(f"     - {folder}")
        
        if not date_folders:
            print("❌ Could not find or create data folders for the specified date range!")
            print("💡 Check file permissions and disk space")
            return
        
        # 3. Find all combined data files and filter by date range and existing dates
        all_combined_files = []
        skipped_files = []
        
        for folder in date_folders:
            combined_files = list(folder.glob("combined_data_*.json"))
            folder_files = []
            folder_skipped = []
            folder_out_of_range = []
            
            for file_path in combined_files:
                file_date = extract_date_from_filename(file_path.name)
                
                if file_date is None:
                    print(f"   ⚠️  Could not parse date from {file_path.name}")
                    continue  # Skip files we can't parse
                
                # Check if file date is within our requested range
                if file_date < start_date or file_date > end_date:
                    folder_out_of_range.append(file_path)
                    continue  # Skip files outside date range
                
                # Check if data already exists for this date
                if not clear_existing and not dry_run and file_date in existing_dates:
                    folder_skipped.append(file_path)  # Skip - already exists
                else:
                    folder_files.append(file_path)  # Include - new data or clearing
            
            all_combined_files.extend(folder_files)
            skipped_files.extend(folder_skipped)
            
            print(f"   {folder.name}: {len(folder_files)} files to load", end="")
            if folder_skipped:
                print(f", {len(folder_skipped)} files skipped (exist)", end="")
            if folder_out_of_range:
                print(f", {len(folder_out_of_range)} files out of range", end="")
            print()  # New line
        
        all_combined_files.sort()
        skipped_files.sort()
        
        print(f"\n   📊 File Summary:")
        print(f"     Files to load: {len(all_combined_files)}")
        print(f"     Files skipped: {len(skipped_files)} (already in database)")
        print(f"     Total files found: {len(all_combined_files) + len(skipped_files)}")
        
        if skipped_files and not dry_run:
            print(f"   📝 Sample skipped files (already loaded):")
            for skip_file in skipped_files[:3]:  # Show first 3
                file_date = extract_date_from_filename(skip_file.name)
                print(f"     - {skip_file.name} (date: {file_date})")
            if len(skipped_files) > 3:
                print(f"     ... and {len(skipped_files) - 3} more")
        
        print(f"\n   Total combined data files: {len(all_combined_files)}")
        
        if not date_folders:
            print("❌ No data folders found for the specified date range!")
            print("💡 Make sure you've extracted data for this period first")
            return
        elif not all_combined_files:
            if len(skipped_files) > 0:
                print("✅ All files in date range already exist in database!")
                print("💡 Use --clear to force reload existing data")
                if not dry_run:
                    # Still show verification of existing data
                    print(f"\n📊 Verifying existing data for {start_date} to {end_date}...")
                    
                    # Check games
                    games_count = db.fetch_results("""
                    SELECT COUNT(*) as count
                    FROM games 
                    WHERE game_date >= :start_date AND game_date <= :end_date
                    """, {"start_date": start_date, "end_date": end_date})[0][0]
                    print(f"   Games in database: {games_count}")
                    
                    # Check boxscore records
                    boxscore_count = db.fetch_results("""
                    SELECT COUNT(*) as count
                    FROM boxscore b
                    INNER JOIN games g ON b.game_id = g.game_id
                    WHERE g.game_date >= :start_date AND g.game_date <= :end_date
                    """, {"start_date": start_date, "end_date": end_date})[0][0]
                    print(f"   Boxscore records in database: {boxscore_count}")
                    
                    print(f"\n✅ No loading needed - data already exists!")
                return
            else:
                print("❌ No combined data files found!")
                
                if auto_extract:
                    print("🚀 AUTO-EXTRACTION ENABLED: Will extract missing data automatically")
                    
                    if not dry_run:
                        # Ask for confirmation for large date ranges
                        date_diff = (end_date - start_date).days
                        if date_diff > 30:
                            print(f"⚠️  Large extraction requested: {date_diff} days")
                            print("   This may take a significant amount of time")
                            response = input("   Continue with automatic extraction? (y/N): ").strip().lower()
                            if response != 'y':
                                print("   Extraction cancelled - showing manual options instead")
                                auto_extract = False
                        
                        if auto_extract:
                            print("� Starting automatic data extraction...")
                            extraction_stats = extract_missing_data(start_date, end_date, dry_run=False)
                            
                            if 'error' in extraction_stats:
                                print(f"❌ Extraction failed: {extraction_stats['error']}")
                                return
                            
                            print(f"\n🔄 Extraction completed! Rescanning for files...")
                            
                            # Rescan for files after extraction
                            all_combined_files = []
                            
                            for folder in date_folders:
                                combined_files = list(folder.glob("combined_data_*.json"))
                                folder_files = []
                                
                                for file_path in combined_files:
                                    file_date = extract_date_from_filename(file_path.name)
                                    
                                    if file_date is None or file_date < start_date or file_date > end_date:
                                        continue  # Skip files we can't parse or are outside range
                                    
                                    # Check if data already exists for this date (if not clearing)
                                    if not clear_existing and file_date in existing_dates:
                                        continue  # Skip - already exists
                                    else:
                                        folder_files.append(file_path)  # Include - new data
                                
                                all_combined_files.extend(folder_files)
                                print(f"   {folder.name}: Found {len(folder_files)} new files after extraction")
                            
                            all_combined_files.sort()
                            print(f"\n   📊 After extraction: {len(all_combined_files)} files ready to load")
                            
                            if not all_combined_files:
                                print("❌ Still no files found after extraction - check extraction logs")
                                return
                    else:
                        print("🔍 DRY RUN: Would extract missing data automatically")
                        extract_missing_data(start_date, end_date, dry_run=True)
                        return
                
                if not auto_extract:
                    print("💡 Manual extraction options:")
                    print("   Run extraction first, then retry this command")
                    
                    # Suggest extraction commands based on date range
                    if start_date.year == 2025:
                        month_name = start_date.strftime("%B").lower()
                        if start_date.month == end_date.month:
                            print(f"   python extract_{month_name}_2025.py")
                        else:
                            print(f"   # Extract data for {start_date.strftime('%B')} - {end_date.strftime('%B')} {start_date.year}")
                            
                    print(f"   # Or use a custom extraction script:")
                    print(f"   # Call extract_season_data(year={start_date.year}, start_date='{start_date}', end_date='{end_date}')")
                    return
        
        if dry_run:
            print(f"\n🔍 DRY RUN SUMMARY:")
            print(f"   Would load {len(all_combined_files)} new files")
            print(f"   Would skip {len(skipped_files)} existing files") 
            print(f"   Date folders: {len(date_folders)}")
            print(f"   Date range: {start_date} to {end_date}")
            if not clear_existing and len(existing_dates) > 0:
                print(f"   Incremental mode: Only loading missing dates")
            return
        
        # 4. Initialize JSON loader with enhanced schema
        loader = JSONToSQLLoader()
        
        # 5. Load each file
        print(f"\n3. Loading {len(all_combined_files)} files...")
        
        success_count = 0
        error_count = 0
        
        for i, file_path in enumerate(all_combined_files, 1):
            try:
                print(f"   [{i}/{len(all_combined_files)}] Loading {file_path.name}...")
                
                # Load the combined data file
                loader.load_json_to_database(str(file_path))
                success_count += 1
                
                if i % 50 == 0:  # Progress update every 50 files
                    print(f"   Progress: {i}/{len(all_combined_files)} files processed")
                
            except Exception as e:
                print(f"   ❌ Error loading {file_path.name}: {e}")
                error_count += 1
        
        print(f"\n4. Loading completed!")
        print(f"   ✅ Successfully loaded: {success_count} files")
        print(f"   ❌ Errors: {error_count} files")
        
        # 6. Verify the loaded data
        print(f"\n5. Verifying loaded data for {start_date} to {end_date}...")
        
        # Check games
        games_count = db.fetch_results("""
        SELECT COUNT(*) as count
        FROM games 
        WHERE game_date >= :start_date AND game_date <= :end_date
        """, {"start_date": start_date, "end_date": end_date})[0][0]
        print(f"   Games loaded: {games_count}")
        
        # Check boxscore records
        boxscore_count = db.fetch_results("""
        SELECT COUNT(*) as count
        FROM boxscore b
        INNER JOIN games g ON b.game_id = g.game_id
        WHERE g.game_date >= :start_date AND g.game_date <= :end_date
        """, {"start_date": start_date, "end_date": end_date})[0][0]
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
        WHERE g.game_date >= :start_date AND g.game_date <= :end_date
        """, {"start_date": start_date, "end_date": end_date})[0]
        
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
        
        # Date range summary
        actual_range = db.fetch_results("""
        SELECT MIN(game_date) as min_date, MAX(game_date) as max_date
        FROM games 
        WHERE game_date >= :start_date AND game_date <= :end_date
        """, {"start_date": start_date, "end_date": end_date})[0]
        
        if actual_range[0] and actual_range[1]:
            print(f"   📅 Actual date range in database: {actual_range[0]} to {actual_range[1]}")
        
        print(f"\n🎉 Data loading completed successfully!")
        print(f"✅ Loaded {games_count} games and {boxscore_count} boxscore records")
        print(f"📊 Date range: {start_date} to {end_date}")
        
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if not dry_run:
            db.disconnect()

def main():
    """Main function with command line argument parsing."""
    parser = argparse.ArgumentParser(
        description="Load MLB data for a dynamic date range",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Load June 2025 data (incremental - only new dates)
  python load_dynamic_date_range_data.py --start 2025-06-01 --end 2025-06-30

  # Load entire 2025 season so far (incremental, auto-create missing folders, auto-extract missing data)
  python load_dynamic_date_range_data.py --start 2025-03-01 --end 2025-08-15

  # Add missing dates to existing range (auto-extracts if needed)
  python load_dynamic_date_range_data.py --start 2025-04-01 --end 2025-05-31

  # Dry run to see what would be loaded and extracted
  python load_dynamic_date_range_data.py --start 2025-06-01 --end 2025-06-30 --dry-run

  # Force clear existing data and reload everything  
  python load_dynamic_date_range_data.py --start 2025-06-01 --end 2025-06-30 --clear
  
  # Load without automatically creating folders or extracting data
  python load_dynamic_date_range_data.py --start 2025-08-01 --end 2025-08-15 --no-create-folders --no-auto-extract
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
        '--clear', 
        action='store_true',
        help='Clear existing data in date range before loading (default: incremental loading)'
    )
    
    parser.add_argument(
        '--dry-run', 
        action='store_true',
        help='Show what would be loaded without actually loading data'
    )
    
    parser.add_argument(
        '--no-create-folders', 
        action='store_true',
        help='Do not automatically create missing month folders'
    )
    
    parser.add_argument(
        '--no-auto-extract', 
        action='store_true',
        help='Do not automatically extract missing data when no files are found'
    )
    
    args = parser.parse_args()
    
    try:
        start_date = parse_date(args.start)
        end_date = parse_date(args.end)
        
        if start_date > end_date:
            print("❌ Error: Start date must be before or equal to end date")
            sys.exit(1)
        
        # Check if date range is reasonable
        date_diff = (end_date - start_date).days
        if date_diff > 365:
            print(f"⚠️  Large date range: {date_diff} days")
            print("   This may take a long time to process")
            
            if not args.dry_run:
                response = input("Continue? (y/N): ").strip().lower()
                if response != 'y':
                    print("Operation cancelled")
                    sys.exit(0)
        
        load_dynamic_date_range_data(
            start_date=start_date,
            end_date=end_date,
            clear_existing=args.clear,
            dry_run=args.dry_run,
            create_folders=not args.no_create_folders,
            auto_extract=not args.no_auto_extract
        )
        
    except ValueError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
