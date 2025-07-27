#!/usr/bin/env python3
"""
MLB Data Pipeline - Main Runner Script
This script sets up the Python path and can run various components of the pipeline.
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Main function to run the pipeline or individual components."""
    if len(sys.argv) > 1:
        component = sys.argv[1].lower()
        
        if component == "extract":
            from src.etl.extract import extract_data
            print("Running extraction...")
            boxscore, game = extract_data(save_json=True)
            if boxscore and game:
                print("✅ Extraction completed successfully!")
                print("📁 JSON files saved in data/json/ directory")
            else:
                print("❌ Extraction failed!")
                
        elif component == "extract-no-json":
            from src.etl.extract import extract_data
            print("Running extraction (no JSON save)...")
            boxscore, game = extract_data(save_json=False)
            if boxscore and game:
                print("✅ Extraction completed successfully!")
            else:
                print("❌ Extraction failed!")
                
        elif component == "setup-db":
            from src.database.connection import DatabaseConnection
            print("Setting up database tables...")
            db = DatabaseConnection()
            if db.connect():
                db.create_tables()
                db.disconnect()
                print("✅ Database setup completed!")
            else:
                print("❌ Database setup failed!")
                
        elif component == "load-json":
            from src.database.json_to_sql_loader import JSONToSQLLoader
            print("Loading JSON files to SQL Server...")
            loader = JSONToSQLLoader()
            if loader.load_all_json_files():
                print("✅ All JSON files loaded successfully!")
            else:
                print("❌ Some files failed to load!")
                
        elif component == "load-schedule":
            from src.api.mlb_client import MLBClient
            from src.database.json_to_sql_loader import JSONToSQLLoader
            from datetime import datetime, timedelta
            
            # Parse arguments for year and month (optional)
            year = 2025
            month = 3
            
            if len(sys.argv) > 2:
                try:
                    year = int(sys.argv[2])
                except ValueError:
                    print("❌ Invalid year format. Use: python run.py load-schedule 2025 3")
                    return
                    
            if len(sys.argv) > 3:
                try:
                    month = int(sys.argv[3])
                except ValueError:
                    print("❌ Invalid month format. Use: python run.py load-schedule 2025 3")
                    return
            
            # Calculate start and end dates for the month
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = datetime(year, month + 1, 1) - timedelta(days=1)
            
            start_date_str = start_date.strftime('%Y-%m-%d')
            end_date_str = end_date.strftime('%Y-%m-%d')
            
            print(f"🗓️  Loading MLB schedule for {start_date.strftime('%B %Y')}")
            print(f"📅 Date range: {start_date_str} to {end_date_str}")
            
            try:
                # Initialize MLB client and loader
                mlb_client = MLBClient()
                loader = JSONToSQLLoader()
                
                # Fetch and load schedule data
                print("🔄 Fetching schedule from MLB API...")
                schedule_data = mlb_client.fetch_schedule(start_date_str, end_date_str)
                
                total_games = sum(len(date_entry.get('games', [])) for date_entry in schedule_data.get('dates', []))
                print(f"📊 Found {total_games} games in schedule")
                
                if total_games > 0:
                    print("💾 Loading schedule data into database...")
                    if loader.load_schedule_data(schedule_data):
                        print(f"✅ Successfully loaded {total_games} games!")
                    else:
                        print("❌ Failed to load schedule data!")
                else:
                    print("⚠️  No games found in the specified date range")
                    
            except Exception as e:
                print(f"❌ Error loading schedule: {e}")
                
        elif component == "extract-and-load":
            # Extract data and immediately load to database
            from src.etl.extract import extract_data
            from src.database.json_to_sql_loader import JSONToSQLLoader
            
            print("Running extraction...")
            boxscore, game = extract_data(save_json=True)
            if boxscore and game:
                print("✅ Extraction completed successfully!")
                print("📁 JSON files saved in data/json/ directory")
                
                print("Loading data to SQL Server...")
                loader = JSONToSQLLoader()
                if loader.load_all_json_files():
                    print("✅ Data loaded to database successfully!")
                else:
                    print("❌ Database loading failed!")
            else:
                print("❌ Extraction failed!")
                
        elif component == "extract-season":
            from src.etl.extract import extract_season_data
            
            # Parse additional arguments
            year = None
            start_date = None
            end_date = None
            
            if len(sys.argv) > 2:
                try:
                    year = int(sys.argv[2])
                except ValueError:
                    print("❌ Invalid year format. Use: python run.py extract-season 2024")
                    return
            
            if len(sys.argv) > 4:
                start_date = sys.argv[3]
                end_date = sys.argv[4]
            
            print(f"Extracting season data for {year or 'current year'}...")
            if start_date and end_date:
                print(f"Date range: {start_date} to {end_date}")
            
            stats = extract_season_data(year=year, start_date=start_date, end_date=end_date)
            if stats['games_extracted'] > 0:
                print("✅ Season extraction completed!")
            else:
                print("❌ No games were extracted!")
                
        elif component == "extract-month":
            from src.etl.extract import extract_season_data
            
            # Parse month and year
            if len(sys.argv) < 4:
                print("Usage: python run.py extract-month YYYY MM")
                print("Example: python run.py extract-month 2024 04")
                return
            
            try:
                year = int(sys.argv[2])
                month = int(sys.argv[3])
                
                # Calculate start and end dates for the month
                from datetime import date
                start_date = date(year, month, 1)
                if month == 12:
                    end_date = date(year + 1, 1, 1) - timedelta(days=1)
                else:
                    end_date = date(year, month + 1, 1) - timedelta(days=1)
                
                print(f"Extracting data for {start_date.strftime('%B %Y')}...")
                stats = extract_season_data(year=year, start_date=start_date, end_date=end_date)
                
                if stats['games_extracted'] > 0:
                    print("✅ Month extraction completed!")
                else:
                    print("❌ No games were extracted!")
                    
            except ValueError:
                print("❌ Invalid date format. Use: python run.py extract-month 2024 04")
                
        elif component == "extract-week":
            from src.etl.extract import extract_season_data
            
            # Parse start date
            if len(sys.argv) < 3:
                print("Usage: python run.py extract-week YYYY-MM-DD")
                print("Example: python run.py extract-week 2024-04-15")
                return
            
            try:
                start_date = datetime.strptime(sys.argv[2], '%Y-%m-%d').date()
                end_date = start_date + timedelta(days=6)
                
                print(f"Extracting data for week: {start_date} to {end_date}...")
                stats = extract_season_data(start_date=start_date, end_date=end_date)
                
                if stats['games_extracted'] > 0:
                    print("✅ Week extraction completed!")
                else:
                    print("❌ No games were extracted!")
                    
            except ValueError:
                print("❌ Invalid date format. Use: python run.py extract-week 2024-04-15")
                
        elif component == "view-db":
            from src.database.connection import DatabaseConnection
            import subprocess
            print("Viewing database contents...")
            try:
                subprocess.run([sys.executable, "view_database.py"], check=True)
            except subprocess.CalledProcessError:
                print("❌ Failed to view database contents")
                
        elif component == "pipeline":
            # Import and run the full pipeline
            from src.main import main as run_pipeline
            run_pipeline()
            
        else:
            print(f"Unknown component: {component}")
            print("Available components: extract, extract-no-json, setup-db, load-json, load-schedule, extract-and-load, view-db, extract-season, extract-month, extract-week, pipeline")
    else:
        print("MLB Data Pipeline")
        print("Usage: python run.py <component>")
        print("Components:")
        print("  extract         - Run data extraction and save JSON files")
        print("  extract-no-json - Run data extraction without saving JSON")
        print("  extract-season  - Extract entire season data (usage: extract-season [year] [start-date] [end-date])")
        print("  extract-month   - Extract month data (usage: extract-month YYYY MM)")
        print("  extract-week    - Extract week data (usage: extract-week YYYY-MM-DD)")
        print("  setup-db        - Setup database tables")
        print("  load-json       - Load JSON files to SQL Server")
        print("  load-schedule   - Load MLB schedule data (usage: load-schedule [year] [month])")
        print("  extract-and-load- Extract data and load to database")
        print("  view-db         - View database contents")
        print("  pipeline        - Run full pipeline")
        print("  setup-db        - Create database tables")
        print("  load-json       - Load existing JSON files to SQL Server")
        print("  extract-and-load- Extract data and load to database")
        print("  view-db         - View database contents")
        print("  pipeline        - Run the full ETL pipeline")

if __name__ == "__main__":
    main()
