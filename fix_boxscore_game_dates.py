#!/usr/bin/env python3
"""
Fix missing game_date values in boxscore table.

This script updates boxscore records that have NULL game_date values
by looking up the correct game_date from the games table.
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database.connection import DatabaseConnection

def fix_boxscore_game_dates():
    """Fix NULL game_date values in boxscore table."""
    
    print("🔧 FIXING BOXSCORE GAME_DATE VALUES")
    print("=" * 50)
    
    db = DatabaseConnection()
    
    try:
        db.connect()
        
        # First, check how many records have NULL game_date
        null_count = db.fetch_results("""
        SELECT COUNT(*) FROM boxscore WHERE game_date IS NULL
        """)[0][0]
        
        print(f"Records with NULL game_date: {null_count}")
        
        if null_count == 0:
            print("✅ No NULL game_date values found - all good!")
            return
        
        # Update NULL game_date values by joining with games table
        print(f"\nUpdating {null_count} records...")
        
        update_query = """
        UPDATE boxscore 
        SET game_date = g.game_date
        FROM boxscore b
        INNER JOIN games g ON b.game_id = g.game_id
        WHERE b.game_date IS NULL
        """
        
        result = db.execute_query(update_query)
        print(f"✅ Update completed!")
        
        # Verify the fix
        remaining_null = db.fetch_results("""
        SELECT COUNT(*) FROM boxscore WHERE game_date IS NULL
        """)[0][0]
        
        print(f"\nVerification:")
        print(f"   Records with NULL game_date now: {remaining_null}")
        
        # Check recent dates now
        recent_dates = db.fetch_results("""
        SELECT TOP 10 game_date, COUNT(*) as count
        FROM boxscore 
        WHERE game_date > '2025-08-18'
        GROUP BY game_date
        ORDER BY game_date DESC
        """)
        
        print(f"\nRecords after 2025-08-18:")
        total_after = 0
        for row in recent_dates:
            print(f"   {row[0]}: {row[1]} records")
            total_after += row[1]
        
        print(f"\nTotal boxscore records after 2025-08-18: {total_after}")
        
        if total_after > 0:
            print("✅ SUCCESS! Boxscore data is now visible after 2025-08-18")
        else:
            print("❌ Still no data after 2025-08-18 - may need to reload data files")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.disconnect()

if __name__ == "__main__":
    fix_boxscore_game_dates()
