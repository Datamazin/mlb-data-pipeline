#!/usr/bin/env python3
"""
Re-extract March and April 2025 MLB Data with Enhanced Game Type Support

This script re-extracts March and April 2025 data using the current enhanced
extraction code that includes proper game type metadata from the schedule API.

The enhanced extraction includes:
- game_type from schedule API (gameType field)
- official_date from schedule API
- series_description from schedule API
- Proper metadata structure in combined JSON files

This will replace the old March-April data that was extracted before the
game type enhancement was implemented.
"""

import sys
import os
from datetime import datetime, date
from pathlib import Path

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.etl.extract import extract_season_data

class MarchAprilReExtractor:
    def __init__(self):
        self.stats = {
            'start_time': datetime.now(),
            'months_processed': 0,
            'total_days': 0,
            'games_extracted': 0,
            'json_files_created': 0,
            'old_files_backed_up': 0
        }
    
    def backup_existing_data(self):
        """Backup existing March-April data before re-extraction."""
        print("📦 Backing up existing March-April 2025 data...")
        
        backup_dir = Path("data/backup/pre_re_extraction")
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup March data
        march_dir = Path("data/json/2025/03-March")
        if march_dir.exists():
            march_backup = backup_dir / "03-March"
            march_backup.mkdir(exist_ok=True)
            
            march_files = list(march_dir.glob("*.json"))
            for file in march_files:
                backup_file = march_backup / file.name
                backup_file.write_text(file.read_text(encoding='utf-8'), encoding='utf-8')
                self.stats['old_files_backed_up'] += 1
            
            print(f"   ✅ Backed up {len(march_files)} March files")
        
        # Backup April data
        april_dir = Path("data/json/2025/04-April")
        if april_dir.exists():
            april_backup = backup_dir / "04-April"
            april_backup.mkdir(exist_ok=True)
            
            april_files = list(april_dir.glob("*.json"))
            for file in april_files:
                backup_file = april_backup / file.name
                backup_file.write_text(file.read_text(encoding='utf-8'), encoding='utf-8')
                self.stats['old_files_backed_up'] += 1
            
            print(f"   ✅ Backed up {len(april_files)} April files")
        
        print(f"   📦 Total files backed up: {self.stats['old_files_backed_up']}")
        print(f"   📍 Backup location: {backup_dir.absolute()}")
    
    def clear_existing_data(self):
        """Clear existing March-April data to make room for re-extraction."""
        print("\n🗑️  Clearing existing March-April 2025 data...")
        
        # Clear March data
        march_dir = Path("data/json/2025/03-March")
        if march_dir.exists():
            march_files = list(march_dir.glob("*.json"))
            for file in march_files:
                file.unlink()
            print(f"   ✅ Cleared {len(march_files)} March files")
        
        # Clear April data
        april_dir = Path("data/json/2025/04-April")
        if april_dir.exists():
            april_files = list(april_dir.glob("*.json"))
            for file in april_files:
                file.unlink()
            print(f"   ✅ Cleared {len(april_files)} April files")
    
    def re_extract_march_2025(self):
        """Re-extract March 2025 data with enhanced game type support."""
        print("\n🌱 Re-extracting March 2025 data...")
        print("=" * 45)
        
        march_start = date(2025, 3, 1)
        march_end = date(2025, 3, 31)
        
        try:
            stats = extract_season_data(
                year=2025,
                start_date=march_start,
                end_date=march_end,
                save_json=True,
                delay_seconds=0.8  # Slightly slower to be respectful to API
            )
            
            if stats:
                self.stats['games_extracted'] += stats.get('games_extracted', 0)
                self.stats['json_files_created'] += stats.get('json_files_saved', 0)
                self.stats['total_days'] += stats.get('days_with_games', 0)
                self.stats['months_processed'] += 1
                
                print(f"\n✅ March 2025 re-extraction completed!")
                print(f"   Games extracted: {stats.get('games_extracted', 0)}")
                print(f"   JSON files created: {stats.get('json_files_saved', 0)}")
                return True
            else:
                print(f"\n❌ March 2025 re-extraction failed")
                return False
                
        except Exception as e:
            print(f"\n❌ Error re-extracting March 2025: {e}")
            return False
    
    def re_extract_april_2025(self):
        """Re-extract April 2025 data with enhanced game type support."""
        print("\n🌸 Re-extracting April 2025 data...")
        print("=" * 45)
        
        april_start = date(2025, 4, 1)
        april_end = date(2025, 4, 30)
        
        try:
            stats = extract_season_data(
                year=2025,
                start_date=april_start,
                end_date=april_end,
                save_json=True,
                delay_seconds=0.8  # Slightly slower to be respectful to API
            )
            
            if stats:
                self.stats['games_extracted'] += stats.get('games_extracted', 0)
                self.stats['json_files_created'] += stats.get('json_files_saved', 0)
                self.stats['total_days'] += stats.get('days_with_games', 0)
                self.stats['months_processed'] += 1
                
                print(f"\n✅ April 2025 re-extraction completed!")
                print(f"   Games extracted: {stats.get('games_extracted', 0)}")
                print(f"   JSON files created: {stats.get('json_files_saved', 0)}")
                return True
            else:
                print(f"\n❌ April 2025 re-extraction failed")
                return False
                
        except Exception as e:
            print(f"\n❌ Error re-extracting April 2025: {e}")
            return False
    
    def verify_enhanced_data(self):
        """Verify that the re-extracted data includes proper game type metadata."""
        print("\n🔍 Verifying enhanced data structure...")
        print("=" * 45)
        
        # Check March data
        march_dir = Path("data/json/2025/03-March")
        march_files = list(march_dir.glob("combined_data_*.json")) if march_dir.exists() else []
        
        if march_files:
            import json
            with open(march_files[0], 'r', encoding='utf-8') as f:
                march_sample = json.load(f)
            
            print(f"📋 March sample file: {march_files[0].name}")
            print(f"   game_type: {march_sample.get('game_type')}")
            print(f"   official_date: {march_sample.get('official_date')}")
            print(f"   series_description: {march_sample.get('series_description')}")
            
            has_metadata = (
                march_sample.get('game_type') is not None or
                march_sample.get('official_date') is not None or
                march_sample.get('series_description') is not None
            )
            
            if has_metadata:
                print(f"   ✅ Enhanced metadata detected in March data")
            else:
                print(f"   ⚠️  No enhanced metadata in March data")
        
        # Check April data
        april_dir = Path("data/json/2025/04-April")
        april_files = list(april_dir.glob("combined_data_*.json")) if april_dir.exists() else []
        
        if april_files:
            import json
            with open(april_files[0], 'r', encoding='utf-8') as f:
                april_sample = json.load(f)
            
            print(f"\n📋 April sample file: {april_files[0].name}")
            print(f"   game_type: {april_sample.get('game_type')}")
            print(f"   official_date: {april_sample.get('official_date')}")
            print(f"   series_description: {april_sample.get('series_description')}")
            
            has_metadata = (
                april_sample.get('game_type') is not None or
                april_sample.get('official_date') is not None or
                april_sample.get('series_description') is not None
            )
            
            if has_metadata:
                print(f"   ✅ Enhanced metadata detected in April data")
            else:
                print(f"   ⚠️  No enhanced metadata in April data")
        
        total_files = len(march_files) + len(april_files)
        print(f"\n📊 Re-extraction verification:")
        print(f"   March files: {len(march_files)}")
        print(f"   April files: {len(april_files)}")
        print(f"   Total new files: {total_files}")
        
        return total_files > 0
    
    def generate_summary_report(self):
        """Generate a summary report of the re-extraction process."""
        end_time = datetime.now()
        duration = end_time - self.stats['start_time']
        
        print(f"\n📊 RE-EXTRACTION SUMMARY REPORT")
        print(f"=" * 50)
        print(f"Start time: {self.stats['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Duration: {duration}")
        print(f"")
        print(f"Data processed:")
        print(f"  Months re-extracted: {self.stats['months_processed']}/2")
        print(f"  Days with games: {self.stats['total_days']}")
        print(f"  Games extracted: {self.stats['games_extracted']}")
        print(f"  JSON files created: {self.stats['json_files_created']}")
        print(f"  Old files backed up: {self.stats['old_files_backed_up']}")
        print(f"")
        print(f"Data locations:")
        print(f"  New March data: data/json/2025/03-March/")
        print(f"  New April data: data/json/2025/04-April/")
        print(f"  Backup location: data/backup/pre_re_extraction/")
        print(f"")
        
        if self.stats['months_processed'] == 2 and self.stats['games_extracted'] > 0:
            print(f"🎉 RE-EXTRACTION COMPLETED SUCCESSFULLY!")
            print(f"   March and April 2025 data now includes enhanced game type metadata")
            print(f"   Ready to reload into database with proper game_type values")
        else:
            print(f"⚠️  RE-EXTRACTION PARTIALLY COMPLETED")
            print(f"   Some issues may have occurred during the process")
        
        return self.stats['months_processed'] == 2

def main():
    """Main function to execute the re-extraction process."""
    print("🚀 MLB Data Pipeline: March-April 2025 Re-Extraction")
    print("=" * 60)
    print("Re-extracting with enhanced game type metadata support")
    print("")
    
    extractor = MarchAprilReExtractor()
    
    try:
        # Step 1: Backup existing data
        extractor.backup_existing_data()
        
        # Step 2: Clear existing data
        extractor.clear_existing_data()
        
        # Step 3: Re-extract March 2025
        march_success = extractor.re_extract_march_2025()
        
        # Step 4: Re-extract April 2025
        april_success = extractor.re_extract_april_2025()
        
        # Step 5: Verify enhanced data
        if march_success and april_success:
            verification_success = extractor.verify_enhanced_data()
            
            # Step 6: Generate summary report
            final_success = extractor.generate_summary_report()
            
            if final_success and verification_success:
                print(f"\n📋 Next Steps:")
                print(f"   1. Load the re-extracted data into database using:")
                print(f"      python load_dynamic_date_range_data.py --start 2025-03-01 --end 2025-04-30 --clear")
                print(f"   2. Verify game_type values are properly populated")
                print(f"   3. Run analysis to confirm regular season game counts > 120")
                return True
            else:
                print(f"\n⚠️  Re-extraction completed with issues")
                return False
        else:
            print(f"\n❌ Re-extraction failed")
            return False
            
    except Exception as e:
        print(f"\n❌ Re-extraction process failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
