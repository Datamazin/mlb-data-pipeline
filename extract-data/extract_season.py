#!/usr/bin/env python3
"""
MLB Season Data Extractor
This script provides advanced functionality for extracting historical MLB season data.
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime, date, timedelta

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.etl.extract import extract_season_data, get_games_for_date

def create_parser():
    """Create argument parser for season extraction."""
    parser = argparse.ArgumentParser(description='Extract MLB season data')
    
    # Mode selection
    parser.add_argument('mode', choices=['season', 'month', 'week', 'date-range', 'test'],
                       help='Extraction mode')
    
    # Year argument
    parser.add_argument('--year', '-y', type=int, default=datetime.now().year,
                       help='Season year (default: current year)')
    
    # Date arguments
    parser.add_argument('--start-date', '-s', type=str,
                       help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', '-e', type=str,
                       help='End date (YYYY-MM-DD)')
    
    # Month/week specific
    parser.add_argument('--month', '-m', type=int, choices=range(1, 13),
                       help='Month number (1-12)')
    parser.add_argument('--week-start', '-w', type=str,
                       help='Week start date (YYYY-MM-DD)')
    
    # Output options
    parser.add_argument('--no-json', action='store_true',
                       help='Skip saving JSON files')
    parser.add_argument('--output-dir', '-o', type=str, default='data/json',
                       help='Output directory for JSON files')
    
    # API options
    parser.add_argument('--delay', '-d', type=float, default=1.0,
                       help='Delay between API calls in seconds (default: 1.0)')
    parser.add_argument('--max-games-per-day', type=int,
                       help='Limit games per day (useful for testing)')
    
    # Testing options
    parser.add_argument('--test-days', type=int, default=7,
                       help='Number of days to test (default: 7)')
    
    return parser

def extract_season(args):
    """Extract full season data."""
    print(f"🏟️  Extracting {args.year} MLB season data...")
    
    stats = extract_season_data(
        year=args.year,
        save_json=not args.no_json,
        delay_seconds=args.delay,
        max_games_per_day=args.max_games_per_day
    )
    
    return stats

def extract_month(args):
    """Extract month data."""
    if not args.month:
        print("❌ Month is required for month mode. Use --month or -m")
        return None
    
    # Calculate month date range
    start_date = date(args.year, args.month, 1)
    if args.month == 12:
        end_date = date(args.year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(args.year, args.month + 1, 1) - timedelta(days=1)
    
    month_name = start_date.strftime('%B')
    print(f"📅 Extracting {month_name} {args.year} data...")
    
    stats = extract_season_data(
        year=args.year,
        start_date=start_date,
        end_date=end_date,
        save_json=not args.no_json,
        delay_seconds=args.delay,
        max_games_per_day=args.max_games_per_day
    )
    
    return stats

def extract_week(args):
    """Extract week data."""
    if not args.week_start:
        print("❌ Week start date is required for week mode. Use --week-start or -w")
        return None
    
    try:
        start_date = datetime.strptime(args.week_start, '%Y-%m-%d').date()
        end_date = start_date + timedelta(days=6)
        
        print(f"📅 Extracting week data: {start_date} to {end_date}")
        
        stats = extract_season_data(
            start_date=start_date,
            end_date=end_date,
            save_json=not args.no_json,
            delay_seconds=args.delay,
            max_games_per_day=args.max_games_per_day
        )
        
        return stats
        
    except ValueError:
        print("❌ Invalid week start date format. Use YYYY-MM-DD")
        return None

def extract_date_range(args):
    """Extract custom date range."""
    if not args.start_date or not args.end_date:
        print("❌ Both start-date and end-date are required for date-range mode")
        return None
    
    try:
        start_date = datetime.strptime(args.start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(args.end_date, '%Y-%m-%d').date()
        
        print(f"📅 Extracting date range: {start_date} to {end_date}")
        
        stats = extract_season_data(
            start_date=start_date,
            end_date=end_date,
            save_json=not args.no_json,
            delay_seconds=args.delay,
            max_games_per_day=args.max_games_per_day
        )
        
        return stats
        
    except ValueError:
        print("❌ Invalid date format. Use YYYY-MM-DD")
        return None

def test_extraction(args):
    """Test extraction with recent games."""
    print(f"🧪 Testing extraction with last {args.test_days} days...")
    
    end_date = date.today()
    start_date = end_date - timedelta(days=args.test_days - 1)
    
    stats = extract_season_data(
        start_date=start_date,
        end_date=end_date,
        save_json=not args.no_json,
        delay_seconds=args.delay,
        max_games_per_day=args.max_games_per_day or 2  # Limit for testing
    )
    
    return stats

def main():
    """Main function."""
    parser = create_parser()
    args = parser.parse_args()
    
    print("MLB Season Data Extractor")
    print("=" * 50)
    
    # Execute based on mode
    if args.mode == 'season':
        stats = extract_season(args)
    elif args.mode == 'month':
        stats = extract_month(args)
    elif args.mode == 'week':
        stats = extract_week(args)
    elif args.mode == 'date-range':
        stats = extract_date_range(args)
    elif args.mode == 'test':
        stats = test_extraction(args)
    else:
        print(f"❌ Unknown mode: {args.mode}")
        return
    
    if stats:
        # Save extraction report
        report_file = f"extraction_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            import json
            with open(report_file, 'w') as f:
                # Convert datetime objects to strings for JSON serialization
                json_stats = {k: str(v) if isinstance(v, (datetime, date, timedelta)) else v 
                             for k, v in stats.items()}
                json.dump(json_stats, f, indent=2)
            print(f"📄 Extraction report saved to: {report_file}")
        except Exception as e:
            print(f"❌ Could not save report: {e}")

def show_examples():
    """Show usage examples."""
    print("MLB Season Data Extractor - Examples")
    print("=" * 50)
    print()
    print("Extract full 2024 season:")
    print("  python extract_season.py season --year 2024")
    print()
    print("Extract April 2024:")
    print("  python extract_season.py month --year 2024 --month 4")
    print()
    print("Extract a week starting April 15, 2024:")
    print("  python extract_season.py week --week-start 2024-04-15")
    print()
    print("Extract custom date range:")
    print("  python extract_season.py date-range --start-date 2024-04-01 --end-date 2024-04-07")
    print()
    print("Test with recent games (no JSON save, faster):")
    print("  python extract_season.py test --no-json --test-days 3")
    print()
    print("Extract with custom settings:")
    print("  python extract_season.py month --year 2024 --month 6 --delay 0.5 --max-games-per-day 5")

if __name__ == "__main__":
    if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] == '--help'):
        show_examples()
    else:
        main()
